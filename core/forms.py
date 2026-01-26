from django import forms
from .models import IncisoControl, GastoOperativo

class IncisoControlForm(forms.ModelForm):
    class Meta:
        model = IncisoControl
        fields = ['ff', 'programa', 'subprograma', 'nombre', 'nota', 'respaldo', 'asignacion', 'dev_com']
        widgets = {
            'ff': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 11'}),
            'programa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 16'}),
            'subprograma': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 02'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 2+3, PROM'}),
            'nota': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Observaciones'}),
            'respaldo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'asignacion': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'dev_com': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
        labels = {
            'dev_com': 'Devengado + Compromiso',
        }

class GastoOperativoForm(forms.ModelForm):
    class Meta:
        model = GastoOperativo
        fields = ['concepto', 'importe_estimado', 'importe_real']
        widgets = {
            'concepto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Insumos de Limpieza'}),
            'importe_estimado': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'importe_real': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
