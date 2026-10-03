from django import forms
from .models import Producto, DisenoPersonalizado

class ProductoForm(forms.ModelForm):
    # Campo auxiliar amigable para escribir el stock por talla
    texto_stock_tallas = forms.CharField(
        label="Stock por Talla",
        widget=forms.TextInput(attrs={
            'class': 'form-control border-secondary', 
            'placeholder': 'Ej: S:5, M:10, L:2, XL:0',
            # AQUÍ ESTÁ EL TRUCO: Le forzamos el fondo oscuro y el texto claro directamente
            'style': 'background-color: #212529; color: #ffffff;' 
        }),
        help_text="Escribe la talla seguida de dos puntos y la cantidad separadas por comas."
    )

    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio', 'texto_stock_tallas', 'imagen']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control border-secondary', 'style': 'background-color: #212529; color: #ffffff;'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control border-secondary', 'rows': 3, 'style': 'background-color: #212529; color: #ffffff;'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control border-secondary', 'style': 'background-color: #212529; color: #ffffff;'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control border-secondary', 'style': 'background-color: #212529; color: #ffffff;'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si estás editando un producto, recupera el JSON y muéstralo como texto legible
        if self.instance and self.instance.pk and self.instance.stock_tallas:
            pares = [f"{t}:{s}" for t, s in self.instance.stock_tallas.items()]
            self.fields['texto_stock_tallas'].initial = ", ".join(pares)

    def save(self, commit=True):
        producto = super().save(commit=False)
        texto = self.cleaned_data['texto_stock_tallas']
        
        # Convierte el texto "S:5, M:10" en un diccionario {"S": 5, "M": 10}
        stock_dict = {}
        try:
            for item in texto.split(','):
                if ':' in item:
                    talla, cantidad = item.split(':')
                    stock_dict[talla.strip().upper()] = int(cantidad.strip())
        except Exception:
            pass
            
        producto.stock_tallas = stock_dict
        if commit:
            producto.save()
        return producto

#... DISEÑO PARA SUBIR PEDIDO DE POLERA 
class DisenoPersonalizadoForm(forms.ModelForm):
    class Meta:
        model = DisenoPersonalizado
        fields = ['imagen', 'detalle']
        widgets = {
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control bg-dark text-light border-secondary', 'required': 'required'}),
            'detalle': forms.Textarea(attrs={
                'class': 'form-control bg-dark text-light border-secondary', 
                'rows': 3, 
                'placeholder': 'Ej: Quiero este diseño en una polera negra, talla L...'
            }),
        }