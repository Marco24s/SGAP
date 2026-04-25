from django import forms
from .models import Personal, Prenda, Asignacion, TipoPrenda, Dotacion

class PersonalForm(forms.ModelForm):
    class Meta:
        model = Personal
        fields = ['legajo', 'apellido', 'nombre', 'grado', 'unidad', 'rol', 'talle_casco', 'talle_guantes', 'talle_overall', 'talle_botas', 'estado']
        widgets = {
            'legajo': forms.NumberInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'grado': forms.Select(attrs={'class': 'form-select'}),
            'rol': forms.Select(attrs={'class': 'form-select'}),
            'talle_casco': forms.TextInput(attrs={'class': 'form-control'}),
            'talle_guantes': forms.TextInput(attrs={'class': 'form-control'}),
            'talle_overall': forms.TextInput(attrs={'class': 'form-control'}),
            'talle_botas': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    UNIDAD_CHOICES = [
        ('Comando de la Aviación Naval', 'Comando de la Aviación Naval'),
        ('Fuerza Aeronaval N° 1', 'Fuerza Aeronaval N° 1'),
        ('Fuerza Aeronaval N° 2', 'Fuerza Aeronaval N° 2'),
        ('Fuerza Aeronaval N° 3', 'Fuerza Aeronaval N° 3'),
        ('2da Escuadrilla Aeronaval de Caza y Ataque', '2da Escuadrilla Aeronaval de Caza y Ataque'),
        ('1ra Escuadrilla Aeronaval de Helicópteros', '1ra Escuadrilla Aeronaval de Helicópteros'),
        ('2da Escuadrilla Aeronaval de Helicópteros', '2da Escuadrilla Aeronaval de Helicópteros'),
        ('Escuadrilla Aeronaval de Exploración', 'Escuadrilla Aeronaval de Exploración'),
        ('Escuadrilla Aeronaval de Vigilancia Marítima', 'Escuadrilla Aeronaval de Vigilancia Marítima'),
        ('Escuadrilla Aeronaval de Sostén Logístico Móvil', 'Escuadrilla Aeronaval de Sostén Logístico Móvil'),
        ('Escuela de Aviación Naval', 'Escuela de Aviación Naval'),
        ('Base Aeronaval Comandante Espora', 'Base Aeronaval Comandante Espora'),
        ('Base Aeronaval Almirante Zar', 'Base Aeronaval Almirante Zar'),
        ('Base Aeronaval Punta Indio', 'Base Aeronaval Punta Indio'),
        ('Arsenal Aeronaval Comandante Espora', 'Arsenal Aeronaval Comandante Espora'),
        ('Taller Aeronaval Almirante Zar', 'Taller Aeronaval Almirante Zar'),
    ]
    
    unidad = forms.ChoiceField(
        choices=UNIDAD_CHOICES, 
        widget=forms.Select(attrs={'class': 'form-select'})
    )

class PrendaForm(forms.ModelForm):
    class Meta:
        model = Prenda
        fields = ['codigo_interno', 'tipo_prenda', 'descripcion', 'talle', 'estado']
        widgets = {
            'codigo_interno': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_prenda': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            'talle': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tipo_prenda'].required = True

class AsignacionForm(forms.ModelForm):
    class Meta:
        model = Asignacion
        fields = ['personal', 'prenda', 'motivo', 'fecha_entrega']
        widgets = {
            'personal': forms.Select(attrs={'class': 'form-select'}),
            'prenda': forms.Select(attrs={'class': 'form-select'}), # Filter available items in view/init
            'motivo': forms.Select(attrs={'class': 'form-select'}),
            'fecha_entrega': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter only available items for assignment
        self.fields['prenda'].queryset = Prenda.objects.filter(estado='deposito')

class TipoPrendaForm(forms.ModelForm):
    class Meta:
        model = TipoPrenda
        fields = ['nombre', 'categoria', 'vida_util_sugerida']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'vida_util_sugerida': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class DotacionForm(forms.ModelForm):
    class Meta:
        model = Dotacion
        fields = ['rol', 'tipo_prenda', 'cantidad', 'renovacion_int']
        widgets = {
            'rol': forms.Select(attrs={'class': 'form-select'}),
            'tipo_prenda': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control'}),
            'renovacion_int': forms.NumberInput(attrs={'class': 'form-control'}),
        }
