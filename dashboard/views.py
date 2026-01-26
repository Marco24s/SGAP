from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from finance.models import Credito, Asignacion, Compromiso
from core.models import UnidadComponente
from django.db.models import Sum, F

@login_required
def home(request):
    # 1. Global Summaries
    creditos_vigentes = Credito.objects.filter(estado='VIGENTE')
    total_presupuesto = creditos_vigentes.aggregate(Sum('monto_total'))['monto_total__sum'] or 0
    
    # Total Distributed (Asignado)
    # We sum all assignments related to vigorous credits
    total_asignado = Asignacion.objects.filter(credito_origen__in=creditos_vigentes).aggregate(Sum('monto'))['monto__sum'] or 0
    
    # Total Executed (Comprometido)
    total_ejecutado = Compromiso.objects.filter(asignacion__credito_origen__in=creditos_vigentes).aggregate(Sum('monto'))['monto__sum'] or 0
    
    porcentaje_global = (total_ejecutado / total_asignado * 100) if total_asignado > 0 else 0

    # 2. Per-Unit Performance (Semáforo)
    # Get all units with assignments
    unidades_stats = []
    unidades = UnidadComponente.objects.filter(asignaciones__credito_origen__in=creditos_vigentes).distinct()
    
    for u in unidades:
        asignado = Asignacion.objects.filter(uucc=u, credito_origen__in=creditos_vigentes).aggregate(Sum('monto'))['monto__sum'] or 0
        ejecutado = Compromiso.objects.filter(asignacion__uucc=u, asignacion__credito_origen__in=creditos_vigentes).aggregate(Sum('monto'))['monto__sum'] or 0
        pc = (ejecutado / asignado * 100) if asignado > 0 else 0
        
        # Traffic Light Logic
        # New Logic:
        # < 40%: Warning (Subejecución)
        # > 95%: Success (Meta Alcanzada)
        # Else: Normal (En Ejecución)
        
        status_color = "primary" 
        status_label = "En Ejecución"
        
        if pc < 40:
            status_color = "warning"
            status_label = "Subejecución"
        elif pc >= 95:
            status_color = "success"
            status_label = "Meta Alcanzada"
            
        unidades_stats.append({
            'unidad': u,
            'asignado': asignado, # Will be formatted later
            'ejecutado': ejecutado,
            'porcentaje': round(pc, 1),
            'color': status_color,
            'label': status_label
        })

    # Helper for formatting
    def fmt(value):
        # Format as 1,000,000 then swap to 1.000.000 for AR
        return f"{value:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")

    context = {
        'creditos': creditos_vigentes,
        # Formatting handled in template (home.html)
        'total_presupuesto': total_presupuesto,
        'total_asignado': total_asignado,
        'total_ejecutado': total_ejecutado,
        'porcentaje_global': round(porcentaje_global, 1),
        'unidades_stats': [
            {
                'unidad': u['unidad'],
                'asignado': u['asignado'],
                'ejecutado': u['ejecutado'],
                'porcentaje': u['porcentaje'],
                'color': u['color'],
                'label': u['label']
            } for u in unidades_stats
        ]
    }
    return render(request, 'dashboard/home.html', context)
