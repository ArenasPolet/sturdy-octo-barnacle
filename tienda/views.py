import urllib.parse
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from .models import Producto, DisenoPersonalizado
from .forms import ProductoForm, DisenoPersonalizadoForm

def catalogo(request):
    productos = Producto.objects.all()
    return render(request, 'tienda/catalogo.html', {'productos': productos})

def es_admin(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(es_admin, login_url='login')
def agregar_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('catalogo')
    else:
        form = ProductoForm()
    return render(request, 'tienda/agregar_producto.html', {'form': form})


#...vista de edicion poleras
@user_passes_test(es_admin, login_url='login')
def editar_producto(request, id):
    # Buscamos la polera exacta por su ID
    producto = get_object_or_404(Producto, id=id)
    
    if request.method == 'POST':
        # Pasamos el "instance=producto" para decirle a Django que estamos actualizando, no creando
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('catalogo')
    else:
        # Carga el formulario con los datos actuales de la polera
        form = ProductoForm(instance=producto)
        
    return render(request, 'tienda/editar_producto.html', {'form': form, 'producto': producto})


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
    # Traemos todas las cotizaciones ordenadas desde la más nueva a la más vieja
    cotizaciones = DisenoPersonalizado.objects.all().order_by('-fecha')
    return render(request, 'tienda/ver_cotizaciones.html', {'cotizaciones': cotizaciones})