from django.db import models

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
   # Agregamos blank=True para que sea opcional
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=0)
   # Almacena el stock por talla en formato JSON, ej: {"S": 5, "M": 10, "L": 2}
    stock_tallas = models.JSONField(default=dict)
    imagen = models.ImageField(upload_to='productos/')

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

    def __str__(self):
        return f"Diseño Personalizado #{self.id}"