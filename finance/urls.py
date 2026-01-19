from django.urls import path
from . import views
from . import api_views

app_name = 'finance'

urlpatterns = [
    path('distribuir/', views.lista_creditos, name='lista_creditos'),
    path('distribuir/nuevo/', views.nuevo_credito, name='nuevo_credito'),
    path('distribuir/<int:credito_id>/', views.distribuir_credito, name='distribuir_credito'),
    path('modificaciones/', views.lista_modificaciones, name='modificaciones'),
    path('modificaciones/nueva/', views.nueva_modificacion, name='nueva_modificacion'),
    path('autorizaciones/', views.lista_autorizaciones, name='lista_autorizaciones'),
    path('autorizaciones/nueva/', views.nueva_autorizacion, name='nueva_autorizacion'),
    path('simular-ejecucion/', views.simular_ejecucion, name='simular_ejecucion'),
    # HTMX API
    path('api/load-children-classifiers/', views.load_children_classifiers, name='load_children_classifiers'),
    
    # JSON API
    path('api/programs/create/', api_views.create_program, name='api_create_program'),
]
