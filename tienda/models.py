from django.db import models

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
   # Agregamos blank=True para que sea opcional
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=0)
   # Almacena el stock por talla en formato JSON, ej: {"S": 5, "M": 10, "L": 2}
    stock_tallas = models.JSONField(default=dict)
    imagen = models.ImageField(upload_to='productos/')
    categoria = models.CharField(max_length=100, blank=True, null=True, verbose_name="Categoría (Ej: Inglaterra)")
    # Interruptor para ocultar la polera sin borrarla
    activo = models.BooleanField(default=True, verbose_name="Visible en el catálogo")
    
    def __str__(self):
        return self.nombre

    @property
    def precio_formateado(self):
        # Convierte el precio a entero y le coloca puntos en los miles
        return f"{int(self.precio):,}".replace(",", ".")


class DisenoPersonalizado(models.Model):
    imagen = models.ImageField(upload_to='personalizados/')
    detalle = models.TextField(blank=True, help_text="Ej: Talla M, en polera negra...")
    fecha = models.DateTimeField(auto_now_add=True)
    telefono = models.CharField(max_length=15, blank=True, null=True, verbose_name="Número de WhatsApp")
    nombre = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nombre del Cliente")
    def __str__(self):
        return f"Diseño Personalizado #{self.id}"



class Venta(models.Model):
    ESTADOS = (
        ('Confirmada', 'Confirmada (Pagada)'),
        ('Rechazada', 'Rechazada / Cancelada'),
    )
    # Relacionamos la venta con la polera. Si borras la polera a futuro, la venta no se borra.
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True, verbose_name="Polera")
    talla = models.CharField(max_length=10)
    cantidad = models.PositiveIntegerField(default=1)
    precio_total = models.IntegerField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default='Confirmada')
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        nombre_prod = self.producto.nombre if self.producto else "Producto Eliminado"
        return f"{nombre_prod} - {self.talla} ({self.estado})"
    @property
    def stock_disponible(self):
        # Si la polera existe y tiene el diccionario de tallas
        if self.producto and self.producto.stock_tallas:
            # Busca el stock de esta talla específica (si no existe, devuelve 0)
            return self.producto.stock_tallas.get(self.talla, 0)
        return 0


class ImagenExtra(models.Model):
    # Relacionamos esta foto con la polera. Si borras la polera, se borran sus fotos extra.
    producto = models.ForeignKey(Producto, related_name='imagenes_extra', on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='productos_extra/')

    def __str__(self):
        return f"Foto extra de {self.producto.nombre}"