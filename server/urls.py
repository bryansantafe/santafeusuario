from django.contrib import admin
from django.urls import path
from django.urls import include
from django.contrib.auth import views as auth_views
from django.http import HttpResponse
from django.views.generic import RedirectView

def placeholder_reportes(request):
    return HttpResponse("<h1>Panel de Reportes del Cliente</h1><p>Próximamente aquí podrás ver tus consumos.</p><a href='/logout/'>Cerrar sesión</a>")
    
urlpatterns = [

    path('', RedirectView.as_view(url='/login/', permanent=False)),
    
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    
    path('usuarios/', include('clientes.urls')),
    path('liquidaciones/', include('liquidaciones.urls')),
    path('reportes/', placeholder_reportes, name='reportes_cliente'),
    
]
