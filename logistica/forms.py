from django import forms
from .models import Personal, Prenda, Asignacion, TipoPrenda, Dotacion

class PersonalForm(forms.ModelForm):
    class Meta:
        model = Personal
        fields = ['legajo', 'apellido', 'nombre', 'grado', 'unidad', 'rol', 'estado']
        widgets = {
            'legajo': forms.NumberInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'grado': forms.Select(attrs={'class': 'form-select'}),
            'unidad': forms.TextInput(attrs={'class': 'form-control'}),
            'rol': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class PrendaForm(forms.ModelForm):
    class Meta:
        model = Prenda
        fields = ['codigo_interno', 'tipo_prenda', 'descripcion', 'talle', 'estado', 'vida_util_meses']
        widgets = {
            'codigo_interno': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_prenda': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            'talle': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'vida_util_meses': forms.NumberInput(attrs={'class': 'form-control'}),
        }

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
