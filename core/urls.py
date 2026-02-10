from django.urls import path, include
from . import auth_views

app_name = 'core'

from . import views

urlpatterns = [
    path('', views.landing_logistica, name='landing'),
    path('login/', auth_views.login_view, name='login'),
    path('logout/', auth_views.logout_view, name='logout'),
    path('control/', views.control_view, name='control'),
    # path('control/', views.control_placeholder_view, name='control'),
    
    # Rutas CRUD Control
    path('control/inciso/nuevo/', views.inciso_create, name='inciso_create'),
    path('control/inciso/editar/<int:pk>/', views.inciso_edit, name='inciso_edit'),
    path('control/gasto/nuevo/', views.gasto_create, name='gasto_create'),
    path('control/gasto/editar/<int:pk>/', views.gasto_edit, name='gasto_edit'),
    # UUCC Quick Add
    path('uucc/nuevo/', views.create_uucc, name='create_uucc'),
    
    # Placeholders
    path('inciso-4/', views.construction_view, {'title': 'Inciso 4'}, name='inciso_4'),
    path('infraestructura/', views.construction_view, {'title': 'Infraestructura'}, name='infraestructura'),
    path('ropa-trabajo/', views.construction_view, {'title': 'Ropa de Trabajo'}, name='ropa_trabajo'),
    path('equipo-vuelo/', views.construction_view, {'title': 'Equipo de Vuelo'}, name='equipo_vuelo'),

]
