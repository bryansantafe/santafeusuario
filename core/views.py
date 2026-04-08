from django.shortcuts import render, get_object_or_404
from django.db.models import Sum, Count
from django.db.models.functions import ExtractYear
from data.models import Agente, Recurso
from clientes.models import Cliente, Frontera
 # Ajusta al nombre de tu app
import json
from django.contrib.auth.decorators import login_required
@login_required
def dashboard_index(request):
    # 1. Totales para las Cards
    total_agentes = Agente.objects.count()
    total_recursos = Recurso.objects.count()
    capacidad_total = Recurso.objects.aggregate(total=Sum('capacidad_efectiva_neta'))['total'] or 0

    # 2. Datos para Gráfica de Torta (Capacidad por Tecnología)
    datos_tech = Recurso.objects.values('tipo_tecnologia').annotate(
        total=Sum('capacidad_efectiva_neta')
    ).order_by('-total')

    # 3. Datos para Gráfica de Líneas (Agentes registrados por año)
    # Usamos fecha_registro de Agente
    crecimiento = Agente.objects.annotate(year=ExtractYear('fecha_registro')).values('year').annotate(
        cantidad=Count('agente_id')
    ).order_by('year')

    context = {
        
        'total_agentes': total_agentes,
        'total_recursos': total_recursos,
        'capacidad_total': round(capacidad_total, 2),

        'labels_tech': json.dumps([item['tipo_tecnologia'] for item in datos_tech]),
        'valores_tech': json.dumps([float(item['total']) for item in datos_tech]),

        'labels_crecimiento': json.dumps(
            [item['year'] for item in crecimiento if item['year']]
        ),
        'valores_crecimiento': json.dumps(
            [item['cantidad'] for item in crecimiento if item['year']]
        ),

        'ultimos_agentes': Agente.objects.all().order_by('-fecha_registro')[:5],

    }
    return render(request, 'core/index.html', context)
@login_required
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
# DEBE LLAMARSE IGUAL QUE EN EL URLS.PY
@login_required
def dashboard_index(request): 
    clientes = Cliente.objects.all().order_by('-fecha_register')[:3]
    print(f"DEBUG: Se encontraron {clientes.count()} clientes") # <--- Mira si esto sale en la terminal
    
    context = {
        'ultimos_clientes': clientes,
        'total_clientes': Cliente.objects.count(),
        'total_fronteras': Frontera.objects.count(),
    }
    return render(request, 'core/index.html', context)