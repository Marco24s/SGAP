from django.contrib import admin
from .models import IncisoControl, GastoOperativo, EstructuraProgramatica, UnidadComponente, ClasificadorGasto, FuenteFinanciamiento

@admin.register(EstructuraProgramatica)
class EstructuraProgramaticaAdmin(admin.ModelAdmin):
    list_display = ("nivel", "codigo", "descripcion", "padre")
    list_filter = ("nivel",)
    search_fields = ("codigo", "descripcion")

@admin.register(UnidadComponente)
class UnidadComponenteAdmin(admin.ModelAdmin):
    list_display = ("codigo", "sigla", "nombre", "es_ejecutora")
    search_fields = ("codigo", "nombre", "sigla")

@admin.register(IncisoControl)
class IncisoControlAdmin(admin.ModelAdmin):
    list_display = ("nombre", "respaldo", "asignacion", "dev_com", "saldo", "falta_asignar")
    search_fields = ("nombre",)

@admin.register(GastoOperativo)
class GastoOperativoAdmin(admin.ModelAdmin):
    list_display = ("concepto", "importe_estimado", "importe_real", "saldo")
    search_fields = ("concepto",)
