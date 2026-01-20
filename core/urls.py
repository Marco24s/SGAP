from django.urls import path
from . import auth_views

app_name = 'core'

urlpatterns = [
    path('login/', auth_views.login_view, name='login'),
    path('logout/', auth_views.logout_view, name='logout'),
]
