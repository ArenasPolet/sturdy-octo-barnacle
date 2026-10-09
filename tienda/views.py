import urllib.parse
from django.core.paginator import Paginator
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from .models import Producto, DisenoPersonalizado,Venta,ImagenExtra
from .forms import ProductoForm, DisenoPersonalizadoForm


def catalogo(request):
    # 1. Obtener todas las categorías únicas que no estén vacías
    categorias = Producto.objects.exclude(categoria__isnull=True).exclude(categoria__exact='').values_list('categoria', flat=True).distinct()
    
    # 2. Ver si el cliente hizo clic en alguna categoría específica
    categoria_filtro = request.GET.get('categoria', '')
    
    # 3. Filtrar los productos
    if categoria_filtro:
        # Agregamos activo=True
        productos_lista = Producto.objects.filter(categoria=categoria_filtro, activo=True).order_by('-id')
    else:
        # Y también aquí para ver solo activos
        productos_lista = Producto.objects.filter(activo=True).order_by('-id')
        
    # 4. Paginación (Mantiene 9 fotos por página)
    paginator = Paginator(productos_lista, 9)
    page_number = request.GET.get('page')
    productos = paginator.get_page(page_number)
    
    return render(request, 'tienda/catalogo.html', {
        'productos': productos,
        'categorias': categorias, # Enviamos la lista de categorías
        'categoria_filtro': categoria_filtro # Enviamos la categoría actual para marcar el botón
    })

def es_admin(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(es_admin, login_url='login')
def agregar_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            # 1. Guarda el producto. Django automáticamente usará la PRIMERA foto como portada.
            producto = form.save()
            
            # 2. Capturamos TODAS las fotos que subiste en el botón
            fotos = request.FILES.getlist('imagen')
            
            # 3. Si subiste más de 1 foto, guardamos el resto en la galería
            if len(fotos) > 1:
                for foto in fotos[1:]: # El [1:] ignora la primera foto porque ya es la portada
                    ImagenExtra.objects.create(producto=producto, imagen=foto)
                    
            return redirect('catalogo')
    else:
        form = ProductoForm()
    return render(request, 'tienda/agregar_producto.html', {'form': form})


@user_passes_test(es_admin, login_url='login')
def editar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            producto = form.save()
            
            # Revisamos si el admin subió un nuevo grupo de fotos
            if 'imagen' in request.FILES:
                fotos = request.FILES.getlist('imagen')
                # Si subió más de 1, agregamos el resto a la galería
                if len(fotos) > 1:
                    for foto in fotos[1:]:
                        ImagenExtra.objects.create(producto=producto, imagen=foto)
                        
            return redirect('catalogo')
    else:
        form = ProductoForm(instance=producto)
        
    return render(request, 'tienda/editar_producto.html', {'form': form, 'producto': producto})

@user_passes_test(es_admin, login_url='login')
def eliminar_producto(request, producto_id):
    # Buscamos la polera
    producto = get_object_or_404(Producto, id=producto_id)
    # La "apagamos"
    producto.activo = False
    producto.save()
    
    # Obtenemos la URL exacta en la que estabas antes de hacer clic
    url_anterior = request.META.get('HTTP_REFERER')
    
    # Si Django logra recordar de dónde venías, te devuelve ahí mismo
    if url_anterior:
        return redirect(url_anterior)
        
    # Si por alguna razón no lo recuerda, te manda al catálogo general por defecto
    return redirect('catalogo')



def pedir_personalizado(request):
    if request.method == 'POST':
        form = DisenoPersonalizadoForm(request.POST, request.FILES)
        if form.is_valid():
            diseno = form.save()
            
            # 1. Obtenemos el link absoluto de la imagen subida (ej. http://midominio.com/media/personalizados/foto.jpg)
            foto_url = request.build_absolute_uri(diseno.imagen.url)
            detalle = diseno.detalle if diseno.detalle else "Sin detalles adicionales."
            
            # 2. Armamos el mensaje para WhatsApp
            mensaje = f"Hola, quiero cotizar una polera con un diseño personalizado:\n\n*Detalles:* {detalle}\n*Foto del diseño:* {foto_url}"
            mensaje_codificado = urllib.parse.quote(mensaje)
            
            # 3. Redirigimos directamente al WhatsApp del vendedor
            numero_wsp = "56986234977" #  NÚMERO REAL  DE WSP
            return redirect(f"https://wa.me/{numero_wsp}?text={mensaje_codificado}")
    else:
        form = DisenoPersonalizadoForm()
        
    return render(request, 'tienda/pedir_personalizado.html', {'form': form})


@user_passes_test(es_admin, login_url='login')
def ver_cotizaciones(request):
    # ordenadas de la más reciente a la más antigua
    cotizaciones_lista = DisenoPersonalizado.objects.all().order_by('-fecha')
    
    paginator = Paginator(cotizaciones_lista, 9)
    page_number = request.GET.get('page')
    cotizaciones = paginator.get_page(page_number)
    
    return render(request, 'tienda/ver_cotizaciones.html', {'cotizaciones': cotizaciones})

@user_passes_test(es_admin, login_url='login')
def panel_ventas(request):
    # 1. SI SE ENVÍA EL FORMULARIO PARA REGISTRAR UNA VENTA
    if request.method == 'POST':
        producto_id = request.POST.get('producto')
        talla = request.POST.get('talla')
        cantidad = int(request.POST.get('cantidad', 1))
        estado = request.POST.get('estado')

        producto = Producto.objects.get(id=producto_id)
        precio_total = producto.precio * cantidad

        # Si la venta fue exitosa, descontamos el stock de esa talla
        if estado == 'Confirmada':
            stock_actual = producto.stock_tallas.get(talla, 0)
            producto.stock_tallas[talla] = max(0, stock_actual - cantidad) # max(0) evita números negativos
            producto.save()

        # Guardamos el registro de la venta
        Venta.objects.create(
            producto=producto, talla=talla, cantidad=cantidad, 
            precio_total=precio_total, estado=estado
        )
        return redirect('panel_ventas')

    # 2. MOSTRAR EL HISTORIAL Y LOS FILTROS
    estado_filtro = request.GET.get('estado', '')
    ventas_query = Venta.objects.all().order_by('-fecha')

    # Si se seleccionó un filtro, aplicarlo
    if estado_filtro:
        ventas_query = ventas_query.filter(estado=estado_filtro)

    # Calcular ganancias sumando el total de todas las ventas que están en pantalla y confirmadas
    total_ganado = sum(v.precio_total for v in ventas_query if v.estado == 'Confirmada')

    # Solo muestra las poleras que están activas (no ocultas)
    productos = Producto.objects.filter(activo=True).order_by('-id')

    return render(request, 'tienda/panel_ventas.html', {
        'ventas': ventas_query,
        'productos': productos,
        'estado_filtro': estado_filtro,
        'total_ganado': total_ganado
    })

@user_passes_test(es_admin, login_url='login')
def descontar_stock_rapido(request, producto_id, talla):
    if request.method == 'POST':
        producto = get_object_or_404(Producto, id=producto_id)
        
        # Obtenemos el stock actual de esa talla
        stock_actual = producto.stock_tallas.get(talla, 0)
        
        # Si hay stock, descontamos 1
        if stock_actual > 0:
            producto.stock_tallas[talla] = stock_actual - 1
            producto.save()
            
            # Opcional: También registramos la venta silenciosamente en el historial financiero
            # para que tu Panel de Ventas siga sumando dinero sin que tú tengas que llenarlo a mano
            Venta.objects.create(
                producto=producto, talla=talla, cantidad=1, 
                precio_total=producto.precio, estado='Confirmada'
            )
            
    # Te devolvemos a donde estabas (catálogo)
    url_anterior = request.META.get('HTTP_REFERER')
    if url_anterior:
        return redirect(url_anterior)
    return redirect('catalogo')


@user_passes_test(es_admin, login_url='login')
def cambiar_estado_venta(request, venta_id):
    if request.method == 'POST':
        venta = get_object_or_404(Venta, id=venta_id)
        nuevo_estado = request.POST.get('nuevo_estado')
        
        # Solo hacemos el proceso si el estado realmente cambió
        if venta.estado != nuevo_estado:
            
            # Si se cancela la venta -> DEVOLVEMOS el stock
            if nuevo_estado == 'Rechazada' and venta.estado == 'Confirmada':
                if venta.producto: # Verificamos que la polera no haya sido borrada
                    stock_actual = venta.producto.stock_tallas.get(venta.talla, 0)
                    venta.producto.stock_tallas[venta.talla] = stock_actual + venta.cantidad
                    venta.producto.save()
                    
            # Si se vuelve a confirmar -> DESCONTAMOS el stock de nuevo
            elif nuevo_estado == 'Confirmada' and venta.estado == 'Rechazada':
                if venta.producto:
                    stock_actual = venta.producto.stock_tallas.get(venta.talla, 0)
                    # max(0) evita que el stock quede en números negativos
                    venta.producto.stock_tallas[venta.talla] = max(0, stock_actual - venta.cantidad) 
                    venta.producto.save()
            
            # Guardamos el nuevo estado en el historial
            venta.estado = nuevo_estado
            venta.save()
            
    # Te devolvemos a la página donde estabas (manteniendo los filtros del panel)
    url_anterior = request.META.get('HTTP_REFERER')
    if url_anterior:
        return redirect(url_anterior)
    return redirect('panel_ventas')


def detalle_producto(request, producto_id):
    # Buscamos la polera (solo si está activa)
    producto = get_object_or_404(Producto, id=producto_id, activo=True)
    return render(request, 'tienda/detalle_producto.html', {'producto': producto})