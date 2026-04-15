from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('dashboard/', views.dashboard_index, name='dashboard'),
    path('agente/<str:agente_id>/', views.agente_detalle, name='agente_detalle'),
    
]