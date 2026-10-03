
from django.contrib import admin
from .models import Producto,DisenoPersonalizado

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'stock_tallas')
    search_fields = ('nombre',)


admin.site.register(DisenoPersonalizado)