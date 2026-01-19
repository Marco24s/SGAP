from django.shortcuts import render
from django.http import HttpResponse
from finance.models import Asignacion, Compromiso
from django.db.models import Sum
import csv
from django.utils import timezone

def reporte_estado_mensual(request):
    """
    Generates the 'Estado Crediticio Mensual' report.
    Aggregates assignments and execution by Program > Unit > Classifier.
    """
    # Get all assignments with their related data
    asignaciones = Asignacion.objects.select_related(
        'uucc', 'clasificador_gasto', 'credito_origen', 'credito_origen__programa', 'credito_origen__fuente'
    ).all().order_by('uucc__codigo', 'clasificador_gasto__codigo')
    
    report_data = []
    
    for a in asignaciones:
        ejecutado = a.compromisos.aggregate(Sum('monto'))['monto__sum'] or 0
        saldo = a.monto - ejecutado
        porcentaje = (ejecutado / a.monto * 100) if a.monto > 0 else 0
        
        report_data.append({
            'programa': a.credito_origen.programa,
            'fuente': a.credito_origen.fuente,
            'unidad': a.uucc,
            'clasificador': a.clasificador_gasto,
            'asignado': a.monto,
            'ejecutado': ejecutado,
            'saldo': saldo,
            'porcentaje': round(porcentaje, 1),
            'trimestre': a.trimestre
        })

    context = {
        'fecha': timezone.now(),
        'report_data': report_data
    }
    return render(request, 'dashboard/reports/estado_mensual.html', context)

def export_csv_report(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="estado_crediticio_{timezone.now().date()}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Programa', 'Fuente', 'Unidad', 'Clasificador', 'Trimestre', 'Asignado', 'Ejecutado', 'Saldo', '% Ejecucion'])

    asignaciones = Asignacion.objects.all()
    for a in asignaciones:
        ejecutado = a.compromisos.aggregate(Sum('monto'))['monto__sum'] or 0
        saldo = a.monto - ejecutado
        porcentaje = (ejecutado / a.monto * 100) if a.monto > 0 else 0
        
        writer.writerow([
            str(a.credito_origen.programa),
            str(a.credito_origen.fuente),
            a.uucc.codigo,
            a.clasificador_gasto.codigo,
            a.trimestre,
            a.monto,
            ejecutado,
            saldo,
            round(porcentaje, 1)
        ])

    return response
