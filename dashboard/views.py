from django.shortcuts import render
from finance.models import Credito, Asignacion, Compromiso
from core.models import UnidadComponente
from django.db.models import Sum, F

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
        # > 90% Red (Danger of Overdraft due to pending?) - Or Green? 
        # SRS: "Semáforo de Compromiso: Mostrar % de ejecución... Límites"
        # Let's interpret: < 50% Warning (Idle), > 95% Critical (Full), 50-95 Normal.
        # Actually user wants "Control": 
        # "Alerta Saldos Ociosos": If end of quarter and not used.
        
        status_color = "success" # Green
        if pc < 40:
            status_color = "warning" # Yellow (Under-execution)
        elif pc > 95:
            status_color = "danger" # Red (Near Limit)
            
        unidades_stats.append({
            'unidad': u,
            'asignado': asignado,
            'ejecutado': ejecutado,
            'porcentaje': round(pc, 1),
            'color': status_color
        })

    context = {
        'creditos': creditos_vigentes,
        'total_presupuesto': total_presupuesto,
        'total_asignado': total_asignado,
        'total_ejecutado': total_ejecutado,
        'porcentaje_global': round(porcentaje_global, 1),
        'unidades_stats': unidades_stats
    }
    return render(request, 'dashboard/home.html', context)
