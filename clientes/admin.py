from django.contrib import admin
from .models import Cliente, Frontera

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre_usuario', 'tipo_identificacion', 'numero_identificacion', 'telefono')
    search_fields = ('nombre_usuario', 'numero_identificacion')

@admin.register(Frontera)
class FronteraAdmin(admin.ModelAdmin):
    list_display = ('numero_factura', 'cliente', 'operador_red', 'nivel_tension', 'mercado')
    list_filter = ('operador_red', 'nivel_tension', 'mercado')
    search_fields = ('numero_factura', 'numero_contrato', 'cliente__nombre_usuario')