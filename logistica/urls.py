from django.urls import path
from . import views

app_name = 'logistica'

urlpatterns = [
    # Dashboard / Index
    path('', views.index, name='index'),

    # Personal URLs
    path('personal/', views.personal_list, name='personal_list'),
    path('personal/crear/', views.personal_create, name='personal_create'),
    path('personal/<int:pk>/editar/', views.personal_update, name='personal_update'),

    # Prenda URLs
    path('prendas/', views.prenda_list, name='prenda_list'),
    path('prendas/crear/', views.prenda_create, name='prenda_create'),
    path('prendas/<int:pk>/editar/', views.prenda_update, name='prenda_update'),

    # Asignaciones
    path('asignaciones/', views.asignacion_list, name='asignacion_list'),
    path('asignaciones/nueva/', views.asignacion_create, name='asignacion_create'),
    path('asignaciones/devolver/<int:pk>/', views.asignacion_return, name='asignacion_return'),

    # Reportes
    path('estado_dotacion/', views.estado_dotacion, name='estado_dotacion'),

    # Gestion Tipo Prenda
    path('tipos_prenda/', views.tipo_prenda_list, name='tipo_prenda_list'),
    path('tipos_prenda/crear/', views.tipo_prenda_create, name='tipo_prenda_create'),
    path('tipos_prenda/<int:pk>/editar/', views.tipo_prenda_update, name='tipo_prenda_update'),
    path('tipos_prenda/<int:pk>/eliminar/', views.tipo_prenda_delete, name='tipo_prenda_delete'),

    # Gestion Reglas Dotacion
    path('dotacion/reglas/', views.dotacion_list, name='dotacion_list'),
    path('dotacion/reglas/crear/', views.dotacion_create, name='dotacion_create'),
    path('dotacion/reglas/<int:pk>/editar/', views.dotacion_update, name='dotacion_update'),
    path('dotacion/reglas/<int:pk>/eliminar/', views.dotacion_delete, name='dotacion_delete'),
]
