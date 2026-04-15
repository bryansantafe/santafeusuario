from django.shortcuts import render, get_object_or_404
from django.db.models import Sum, Count
from django.db.models.functions import ExtractYear
from data.models import Agente, Recurso
from clientes.models import Cliente, Frontera
# Ajusta al nombre de tu app
import json
from django.contrib.auth.decorators import login_required,user_passes_test
def es_staff(user):
    return user.is_staff

@login_required
@user_passes_test(es_staff, login_url='/reportes/')
def dashboard_index(request):
    ## 1. Datos de Agentes y Recursos
    total_agentes = Agente.objects.count()
    total_recursos = Recurso.objects.count()
    capacidad_total = Recurso.objects.aggregate(total=Sum('capacidad_efectiva_neta'))['total'] or 0

    datos_tech = Recurso.objects.values('tipo_tecnologia').annotate(
        total=Sum('capacidad_efectiva_neta')
    ).order_by('-total')

    crecimiento = Agente.objects.annotate(year=ExtractYear('fecha_registro')).values('year').annotate(
        cantidad=Count('agente_id')
    ).order_by('year')

    ## 2. Datos de Clientes y Fronteras
    clientes = Cliente.objects.all().order_by('-fecha_register')[:3]
    total_clientes = Cliente.objects.count()
    total_fronteras = Frontera.objects.count()

    context = {
        # Contexto de Agentes
        'total_agentes': total_agentes,
        'total_recursos': total_recursos,
        'capacidad_total': round(capacidad_total, 2),
        'labels_tech': json.dumps([item['tipo_tecnologia'] for item in datos_tech]),
        'valores_tech': json.dumps([float(item['total']) for item in datos_tech]),
        'labels_crecimiento': json.dumps([item['year'] for item in crecimiento if item['year']]),
        'valores_crecimiento': json.dumps([item['cantidad'] for item in crecimiento if item['year']]),
        'ultimos_agentes': Agente.objects.all().order_by('-fecha_registro')[:5],
        
        # Contexto de Clientes
        'ultimos_clientes': clientes,
        'total_clientes': total_clientes,
        'total_fronteras': total_fronteras,
    }
    
    # La ruta al template está perfecta para la nueva arquitectura
    return render(request, 'core/index.html', context)
    
@login_required
@user_passes_test(es_staff, login_url='/reportes/')
def agente_detalle(request, agente_id):
    agente = get_object_or_404(Agente, agente_id=agente_id)
    # Obtenemos los recursos usando la relación reversa
    recursos = Recurso.objects.filter(agente=agente)
    capacidad_agente = recursos.aggregate(total=Sum('capacidad_efectiva_neta'))['total'] or 0

    return render(request, 'core/agente_detalle.html', {
        'agente': agente,
        'recursos': recursos,
        'capacidad_total': capacidad_agente
    })