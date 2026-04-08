from django.urls import path
from . import views

urlpatterns = [
    path('panel/', views.modulo_liquidaciones, name='modulo_liquidaciones'),
    path('contrato/gestionar/', views.gestionar_contrato, name='gestionar_contrato'),
    # NUEVA RUTA PARA VER EL DETALLE DE CONSUMO
    path('consumo/detalle/', views.detalle_consumo, name='detalle_consumo'),
    path('factura/pdf/<int:frontera_id>/<str:fecha_str>/', views.exportar_factura_pdf, name='factura_pdf'),
]