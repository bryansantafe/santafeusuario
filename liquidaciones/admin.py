from django.contrib import admin
from .models import (
    Periodo, Contrato, ComponenteG, ComponenteC, 
    ComponenteD, ComponenteT, ComponentePR, 
    ComponenteR, ConsumoHorario
)

# --- CONFIGURACIÓN DE PERIODOS E ÍNDICES ---
@admin.register(Periodo)
class PeriodoAdmin(admin.ModelAdmin):
    """
    Permite gestionar los índices económicos globales por mes.
    """
    list_display = ('id', 'fecha_mes', 'valor_ipc', 'valor_ipp')
    # Permite editar los índices directamente en la tabla sin entrar al registro
    list_editable = ('valor_ipc', 'valor_ipp')
    list_filter = ('fecha_mes',)
    ordering = ('-fecha_mes',)

# --- CONFIGURACIÓN DE CONTRATOS ---
@admin.register(Contrato)
class ContratoAdmin(admin.ModelAdmin):
    """
    Gestión de los términos comerciales base con el cliente.
    """
    list_display = ('id', 'frontera', 'fecha_inicio', 'tipo_pld', 'precio_g_base', 'precio_c_base')
    list_filter = ('tipo_pld', 'fecha_inicio', 'frontera')
    search_fields = ('frontera__numero_factura',)

# --- COMPONENTES DE GENERACIÓN Y COMERCIALIZACIÓN ---
@admin.register(ComponenteG)
class ComponenteGAdmin(admin.ModelAdmin):
    list_display = ('id', 'contrato', 'periodo', 'valor_base', 'valor_indice', 'valor_indexado')
    list_filter = ('periodo', 'contrato')
    search_fields = ('contrato__frontera__numero_factura',)
    readonly_fields = ('valor_indexado',) # Calculado por el sistema

@admin.register(ComponenteC)
class ComponenteCAdmin(admin.ModelAdmin):
    list_display = ('id', 'contrato', 'periodo', 'valor_base', 'valor_indice', 'valor_indexado')
    list_filter = ('periodo', 'contrato')
    search_fields = ('contrato__frontera__numero_factura',)
    readonly_fields = ('valor_indexado',)

# --- COMPONENTES REGULADOS (DEPENDEN DEL OPERADOR) ---
@admin.register(ComponenteD)
class ComponenteDAdmin(admin.ModelAdmin):
    list_display = ('id', 'periodo', 'operador_red', 'nivel_tension', 'valor')
    list_filter = ('operador_red', 'nivel_tension', 'periodo')
    list_editable = ('valor',)

@admin.register(ComponentePR)
class ComponentePRAdmin(admin.ModelAdmin):
    list_display = ('id', 'periodo', 'operador_red', 'nivel_tension', 'valor')
    list_filter = ('operador_red', 'nivel_tension', 'periodo')
    list_editable = ('valor',)

@admin.register(ComponenteT)
class ComponenteTAdmin(admin.ModelAdmin):
    list_display = ('id', 'periodo', 'operador_red', 'valor')
    list_filter = ('operador_red', 'periodo')
    list_editable = ('valor',)

@admin.register(ComponenteR)
class ComponenteRAdmin(admin.ModelAdmin):
    list_display = ('id', 'periodo', 'operador_red', 'valor')
    list_filter = ('operador_red', 'periodo')
    list_editable = ('valor',)

# --- CONSUMOS HORARIOS ---
@admin.register(ConsumoHorario)
class ConsumoHorarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'frontera', 'fecha', 'hora', 'consumo_activo', 'consumo_reactivo', 'es_estimado')
    list_filter = ('fecha', 'es_estimado', 'frontera')
    search_fields = ('frontera__numero_factura', 'fecha')
    ordering = ('-fecha', 'hora')