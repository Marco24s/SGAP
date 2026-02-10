from django.urls import path
from . import views
from . import reports_views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home, name='home'),
    path('bases-decision/', views.bases_decision, name='bases_decision'),
    path('reportes/estado-mensual/', reports_views.reporte_estado_mensual, name='reporte_estado_mensual'),
    path('reportes/exportar-csv/', reports_views.export_csv_report, name='export_csv'),
]
