from django import forms
from .models import ModificacionPresupuestaria, AutorizacionCargo, Asignacion, UnidadComponente, ClasificadorGasto

class ModificacionForm(forms.ModelForm):
    class Meta:
        model = ModificacionPresupuestaria
        fields = ['origen', 'destino', 'monto']
        widgets = {
            'origen': forms.Select(attrs={'class': 'form-input'}),
            'destino': forms.Select(attrs={'class': 'form-input'}),
            'monto': forms.NumberInput(attrs={'class': 'form-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        origen = cleaned_data.get('origen')
        destino = cleaned_data.get('destino')
        monto = cleaned_data.get('monto')

        if origen and destino and monto:
            # 1. Check funds
            if origen.monto < monto:
                self.add_error('monto', f"Fondos insuficientes en origen. Disponible: {origen.monto}")
            
            # 2. Determine Type (Logic moved to View/Save, but validated here if needed)
            if origen.credito_origen.programa == destino.credito_origen.programa:
                self.instance.tipo = 'REDISTRIBUCION' # Internal
                self.instance.estado = 'APROBADO' # Auto-approve for MVP/Demo
            else:
                self.instance.tipo = 'ENTRE_PROGRAMAS'
                self.instance.estado = 'PENDIENTE'

        return cleaned_data

class AutorizacionCargoForm(forms.ModelForm):
    class Meta:
        model = AutorizacionCargo
        fields = ['unidad_origen', 'unidad_autorizada', 'clasificador', 'monto_maximo', 'vencimiento']
        widgets = {
            'unidad_origen': forms.Select(attrs={'class': 'form-input'}),
            'unidad_autorizada': forms.Select(attrs={'class': 'form-input'}),
            'clasificador': forms.Select(attrs={'class': 'form-input'}),
            'monto_maximo': forms.NumberInput(attrs={'class': 'form-input'}),
            'vencimiento': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
        }

from .models import Credito
class CreditoForm(forms.ModelForm):
    class Meta:
        model = Credito
        fields = ['programa', 'fuente', 'anio', 'trimestre', 'monto_total', 'monto_cuota', 'recibido', 'inciso', 'principal', 'tipo_credito']
        widgets = {
            'monto_total': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-input', 'placeholder': 'Ej: 15000000'}),
            'monto_cuota': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-input', 'placeholder': 'Ej: 5000000'}),
            'recibido': forms.CheckboxInput(attrs={'class': 'form-checkbox', 'style': 'width: 1.25rem; height: 1.25rem;'}),
            'inciso': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej: 2'}),
            'principal': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej: 1'}),
            'programa': forms.Select(attrs={'class': 'form-input'}),
            'fuente': forms.Select(attrs={'class': 'form-input'}),
            'anio': forms.NumberInput(attrs={'class': 'form-input', 'value': 2026}),
            'trimestre': forms.Select(attrs={'class': 'form-input'}),
            'tipo_credito': forms.Select(attrs={'class': 'form-input'}),
        }
