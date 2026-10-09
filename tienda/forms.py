from django import forms
from django.core.exceptions import ValidationError
import re
from .models import Producto, DisenoPersonalizado



class MultipleFileInput(forms.FileInput):
    allow_multiple_selected = True

    def value_from_datadict(self, data, files, name):
        # TRUCO MAESTRO: Interceptamos las fotos cuando Django las está leyendo
        if hasattr(files, 'getlist'):
            archivos = files.getlist(name)
            if archivos:
                # Le entregamos SOLO LA PRIMERA a la validación principal para que no colapse.
                # (En el views.py igual podremos capturarlas todas).
                return archivos[0]
        return None

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
        fields = ['nombre','categoria', 'descripcion', 'precio', 'imagen', 'texto_stock_tallas']
        labels = {
            'imagen': '📸 Imágenes de la Polera (Puedes seleccionar varias)',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control border-secondary', 'style': 'background-color: #212529; color: #ffffff;'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control border-secondary', 'rows': 3, 'style': 'background-color: #212529; color: #ffffff;'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control border-secondary', 'style': 'background-color: #212529; color: #ffffff;'}),
            'imagen': MultipleFileInput(attrs={
                'class': 'form-control border-secondary', 
                'style': 'background-color: #212529; color: #ffffff;'
            }),
        
            'categoria': forms.TextInput(attrs={
                'class': 'form-control border-secondary', 
                'placeholder': 'Ej: Inglaterra, España, Selecciones...', 
                'style': 'background-color: #212529; color: #ffffff;'
            }),
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
        fields = ['imagen', 'detalle','nombre','telefono']
        widgets = {
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control bg-dark text-light border-secondary', 'required': 'required'}),
            'detalle': forms.Textarea(attrs={
                'class': 'form-control bg-dark text-light border-secondary', 
                'rows': 3, 
                'placeholder': 'Ej: Quiero este diseño en una polera negra, talla L...'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control border-secondary', 
                'pattern': '[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+',
                'title': 'Solo se permiten letras y espacios',
                'placeholder': 'Ej: Juan Pérez',
                'style': 'background-color: #212529; color: #ffffff;'
            }),
            # Agregamos el diseño para el teléfono
            'telefono': forms.TextInput(attrs={
                'class': 'form-control border-secondary', 
                'type': 'number',         # Fuerza el teclado numérico
                'pattern': '[0-9]*',      # Solo permite números
                'placeholder': 'Ej: +56912345678',
                'style': 'background-color: #212529; color: #ffffff;'
            }),
        }

    # 2. LA VALIDACIÓN DE SEGURIDAD: Python revisa el dato antes de guardarlo
    def clean_nombre(self):
        # Capturamos lo que el cliente escribió en el campo "nombre"
        nombre = self.cleaned_data.get('nombre')
        
        # Revisamos si contiene algo que no sean letras, acentos, ñ o espacios
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', nombre):
            # Si tiene números o símbolos raros, Django bloquea el guardado y lanza este error
            raise ValidationError("El nombre solo puede contener letras y espacios. No uses números ni símbolos.")
            
        return nombre

#  función para que los campos sean obligatorios en la página
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Hacemos que nombre, teléfono e imagen sean 100% obligatorios
        self.fields['nombre'].required = True
        self.fields['telefono'].required = True
        self.fields['imagen'].required = True
        
        # El detalle queda opcional por si la imagen ya lo explica todo
        self.fields['detalle'].required = False