from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_clientes, name='lista_clientes'), # Este es el nombre clave
    path('nuevo/', views.crear_cliente, name='crear_cliente'),
    path('<int:cliente_id>/', views.detalle_cliente, name='detalle_cliente'),
]