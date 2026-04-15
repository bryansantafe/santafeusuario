## clientes/urls.py
from django.urls import path
from . import views
from .views import aceptar_terminos, detalle_cliente, crear_cliente, lista_clientes
from django.contrib.auth import views as auth_views

app_name = 'clientes'

urlpatterns = [
    path('', lista_clientes, name='lista_clientes'), # Este es el nombre clave
    path('nuevo/', crear_cliente, name='crear_cliente'),
    path('<int:cliente_id>/', detalle_cliente, name='detalle_cliente'),
    path('aceptar-terminos/', aceptar_terminos, name='aceptar_terminos'),
    path('cambiar-password/', auth_views.PasswordChangeView.as_view(
        template_name='core/cambiar_password.html', 
        success_url='/'
    ), name='cambiar_password'),
]