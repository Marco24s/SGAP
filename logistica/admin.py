from django.contrib import admin
from .models import Personal, Prenda, Asignacion, Movimiento, TipoPrenda, Dotacion

@admin.register(TipoPrenda)
class TipoPrendaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'vida_util_sugerida')
    search_fields = ('nombre',)

@admin.register(Dotacion)
class DotacionAdmin(admin.ModelAdmin):
    list_display = ('rol', 'tipo_prenda', 'cantidad', 'renovacion_int')
    list_filter = ('rol',)
    search_fields = ('rol', 'tipo_prenda__nombre')

@admin.register(Personal)
class PersonalAdmin(admin.ModelAdmin):
    list_display = ('legajo', 'grado', 'apellido', 'nombre', 'rol', 'estado')
    search_fields = ('legajo', 'apellido', 'nombre')
    list_filter = ('grado', 'rol', 'estado')

@admin.register(Prenda)
class PrendaAdmin(admin.ModelAdmin):
    list_display = ('codigo_interno', 'tipo_prenda', 'descripcion', 'talle', 'estado', 'vida_util_meses')
    search_fields = ('codigo_interno', 'descripcion')
    list_filter = ('tipo_prenda', 'estado')

@admin.register(Asignacion)
class AsignacionAdmin(admin.ModelAdmin):
    list_display = ('prenda', 'personal', 'fecha_entrega', 'motivo', 'active_status')
    search_fields = ('prenda__codigo_interno', 'personal__apellido')
    list_filter = ('motivo',)
    
    def active_status(self, obj):
        return "Activa" if obj.fecha_devolucion is None else "Devuelta"
    active_status.short_description = 'Estado'

@admin.register(Movimiento)
class MovimientoAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'tipo', 'prenda', 'usuario')
    list_filter = ('tipo', 'fecha')
    search_fields = ('prenda__codigo_interno',)
