from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from finance.models import Credito, Asignacion, Compromiso
from core.models import UnidadComponente
from django.db.models import Sum, F

@login_required
def home(request):
    # 1. Global Summaries
    creditos_vigentes = Credito.objects.filter(estado='VIGENTE')
    
    # Calculate Total Budget ignoring duplicate Quotas for same Program/Inciso/Year
    total_presupuesto = 0
    seen_budgets = set()
    
    # Group credits for display
    # Key: (programa_id, fuente_id, inciso, anio)
    grouped_credits = {}
    
    for c in creditos_vigentes:
        # Key for Deduplication / Grouping
        # Include principal and tipo_credito to separate them correctly
        key = (c.programa_id, c.fuente_id, c.inciso, c.principal, c.anio, c.tipo_credito)
        
        # 1. Calculate Total Budget (Techo)
        if key not in seen_budgets:
            total_presupuesto += c.monto_total
            seen_budgets.add(key)
            
        # 2. Group for Table Display
        if key not in grouped_credits:
            grouped_credits[key] = {
                'programa': c.programa, # Object for display
                'fuente': c.fuente,     # Object for display
                'inciso': c.inciso,
                'principal': c.principal,
                'anio': c.anio,
                'techo': c.monto_total,
                'quarters': {} 
            }
        
        # Add quarter info
        # We store a list of credits for the same quarter to handle both Asignación and Refuerzo
        if c.trimestre not in grouped_credits[key]['quarters']:
            grouped_credits[key]['quarters'][c.trimestre] = []
            
        grouped_credits[key]['quarters'][c.trimestre].append({
            'amount': c.monto_cuota, # Display Quota Amount
            'id': c.id,
            'recibido': c.recibido,
            'tipo': c.tipo_credito
        })
    
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

    context = {
        'creditos': grouped_credits.values(), # Pass the list of grouped dicts
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

@login_required
def bases_decision(request):
    return render(request, 'dashboard/bases_decision.html')

