from django.contrib import admin
from .models import (
    Agente, Recurso, MetricasMercadoPrecios, 
    MetricasTransaccionesLiquidacion, MetricasDemandaBalance
)

# 1. Registro simple para modelos básicos
admin.site.register(Agente)
admin.site.register(Recurso)

@admin.register(MetricasMercadoPrecios)
class PreciosAdmin(admin.ModelAdmin):
    list_display = ('fecha_operacion', 'periodo_hora', 'precio_bolsa_nacional', 'trm_dia')
    list_filter = ('fecha_operacion',)
    ordering = ('-fecha_operacion', 'periodo_hora')