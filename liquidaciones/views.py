import json
import statistics
from decimal import Decimal
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from django.db import transaction
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from weasyprint import HTML

from clientes.models import Cliente, Frontera
from .models import (
    Contrato, Periodo, ConsumoHorario,
    ComponenteG, ComponenteC, ComponenteD, ComponenteT, 
    ComponentePR, ComponenteR
)

# ==========================================
# FUNCIÓN HELPER: CENTRALIZA EL CÁLCULO
# ==========================================
def obtener_liquidacion_mes(frontera, fecha_periodo, total_energia):
    """
    Busca los componentes G, T, D, C, PR, R vigentes para una frontera en un mes
    específico y retorna el diccionario de componentes, el CU y el Total.
    """
    periodo_m = Periodo.objects.filter(fecha_mes__lte=fecha_periodo).order_by('-fecha_mes').first()
    contrato = Contrato.objects.filter(frontera=frontera).order_by('-fecha_inicio').first()
    
    componentes = {
        'G (Generación)': Decimal('0.00'), 'T (Transmisión)': Decimal('0.00'),
        'D (Distribución)': Decimal('0.00'), 'PR (Pérdidas)': Decimal('0.00'),
        'R (Restricciones)': Decimal('0.00'), 'C (Comercializ.)': Decimal('0.00'),
    }
    
    if contrato and periodo_m:
        g_obj = ComponenteG.objects.filter(contrato=contrato, periodo__fecha_mes__lte=periodo_m.fecha_mes).order_by('-periodo__fecha_mes').first()
        c_obj = ComponenteC.objects.filter(contrato=contrato, periodo__fecha_mes__lte=periodo_m.fecha_mes).order_by('-periodo__fecha_mes').first()
        t = ComponenteT.objects.filter(periodo=periodo_m, operador_red=frontera.operador_red).first()
        r = ComponenteR.objects.filter(periodo=periodo_m, operador_red=frontera.operador_red).first()
        d = ComponenteD.objects.filter(periodo=periodo_m, operador_red=frontera.operador_red, nivel_tension=frontera.nivel_tension).first()
        pr = ComponentePR.objects.filter(periodo=periodo_m, operador_red=frontera.operador_red, nivel_tension=frontera.nivel_tension).first()

        componentes['G (Generación)'] = g_obj.valor_indexado if g_obj else Decimal('0.00')
        componentes['C (Comercializ.)'] = c_obj.valor_indexado if c_obj else Decimal('0.00')
        componentes['T (Transmisión)'] = t.valor if t else Decimal('0.00')
        componentes['R (Restricciones)'] = r.valor if r else Decimal('0.00')
        componentes['D (Distribución)'] = d.valor if d else Decimal('0.00')
        componentes['PR (Pérdidas)'] = pr.valor if pr else Decimal('0.00')

    cu_variable = sum(componentes.values())
    total_a_facturar = total_energia * cu_variable
    
    return {
        'componentes': componentes,
        'cu_variable': cu_variable,
        'total_a_facturar': total_a_facturar
    }

# ==========================================
# VISTAS PRINCIPALES
# ==========================================

@login_required
def modulo_liquidaciones(request):
    usuario_id = request.GET.get('usuario')
    frontera_id = request.GET.get('frontera')
    clientes = Cliente.objects.all().order_by('nombre_usuario')
    
    for c in clientes: c.is_selected = str(c.id) == usuario_id

    fronteras, contrato_actual, no_contrato = None, None, False
    
    if usuario_id:
        fronteras = list(Frontera.objects.filter(cliente_id=usuario_id))
        for f in fronteras:
            f.is_selected = str(f.id) == frontera_id
            if f.is_selected:
                contrato_actual = Contrato.objects.filter(frontera_id=f.id).order_by('-fecha_inicio').first()

    if frontera_id and not contrato_actual:
        no_contrato = True

    return render(request, 'liquidaciones/panel.html', {
        'clientes': clientes, 'fronteras': fronteras, 'contrato': contrato_actual,
        'frontera_id': frontera_id, 'no_contrato': no_contrato,
    })

@login_required
def gestionar_contrato(request):
    frontera_id = request.POST.get('frontera') or request.GET.get('frontera')
    error_msj = None
    
    if not frontera_id:
        return redirect('modulo_liquidaciones')
        
    frontera = Frontera.objects.filter(id=frontera_id).first()
    contrato = Contrato.objects.filter(frontera_id=frontera_id).order_by('-fecha_inicio').first()
    
    def clean_decimal(value):
        if not value or str(value).strip() == '': return Decimal('1.00')
        return Decimal(str(value).replace(',', '.').strip())

    if request.method == "POST":
        c_id = request.POST.get('contrato_id')
        
        if 'eliminar_contrato' in request.POST:
            Contrato.objects.filter(frontera_id=frontera_id).delete()
            return redirect(f"/liquidaciones/panel/?usuario={frontera.cliente.id}&frontera={frontera_id}")

        try:
            with transaction.atomic():
                f_inicio = request.POST.get('fecha_inicio')
                defaults_contrato = {
                    'fecha_inicio': f_inicio,
                    'fecha_fin': request.POST.get('fecha_fin'),
                    'tipo_pld': request.POST.get('tipo_pld') or 'FIJO',
                    'precio_g_base': clean_decimal(request.POST.get('g_base')),
                    'precio_c_base': clean_decimal(request.POST.get('c_base')),
                    'ipp_base': clean_decimal(request.POST.get('ipp_base')),
                    'ipc_base': clean_decimal(request.POST.get('ipc_base')),
                }
                
                if c_id:
                    Contrato.objects.filter(id=c_id).update(**defaults_contrato)
                    contrato_guardado = Contrato.objects.get(id=c_id)
                else:
                    contrato_guardado = Contrato.objects.create(frontera=frontera, **defaults_contrato)

                # GUARDAR COMPONENTES (La matemática ahora la hace el models.py)
                if f_inicio:
                    fecha_dt = datetime.strptime(f_inicio, '%Y-%m-%d') 
                    periodo_obj, _ = Periodo.objects.get_or_create(fecha_mes=fecha_dt.replace(day=1).date())
                    
                    ComponenteG.objects.update_or_create(
                        contrato=contrato_guardado, periodo=periodo_obj, 
                        defaults={
                            'valor_base': contrato_guardado.precio_g_base, 
                            'tipo_indice': request.POST.get('g_tipo_indice'),
                            'fecha_indice': request.POST.get('g_fecha_indice') or None,
                        }
                    )
                    
                    ComponenteC.objects.update_or_create(
                        contrato=contrato_guardado, periodo=periodo_obj, 
                        defaults={
                            'valor_base': contrato_guardado.precio_c_base, 
                            'tipo_indice': request.POST.get('c_tipo_indice'),
                            'fecha_indice': request.POST.get('c_fecha_indice') or None,
                        }
                    )

                return redirect(f"/liquidaciones/consumo/detalle/?frontera={frontera_id}&fecha={f_inicio[:7]}")
        except Exception as e:
            error_msj = f"Error al guardar: {str(e)}"

    g_actual = ComponenteG.objects.filter(contrato=contrato).first() if contrato else None
    c_actual = ComponenteC.objects.filter(contrato=contrato).first() if contrato else None

    context = {
        'frontera': frontera, 'contrato': contrato,
        'g_actual': g_actual, 'c_actual': c_actual,
        'opciones_pld': [
            {'val': 'FIJO', 'active': bool(contrato and contrato.tipo_pld == 'FIJO')},
            {'val': 'BOLSA', 'active': bool(contrato and contrato.tipo_pld == 'BOLSA')},
            {'val': 'FORMULA', 'active': bool(contrato and contrato.tipo_pld == 'FORMULA')},
        ],
        'opciones_g': [
            {'val': 'IPP', 'active': bool(g_actual and g_actual.tipo_indice == 'IPP')},
            {'val': 'IPC', 'active': bool(g_actual and g_actual.tipo_indice == 'IPC')},
        ],
        'opciones_c': [
            {'val': 'IPP', 'active': bool(c_actual and c_actual.tipo_indice == 'IPP')},
            {'val': 'IPC', 'active': bool(c_actual and c_actual.tipo_indice == 'IPC')},
        ],
        'error_msj': error_msj,
    }
    return render(request, 'liquidaciones/gestionar_contrato.html', context)

@login_required
def detalle_consumo(request):
    frontera_id = request.GET.get('frontera')
    fecha_str = request.GET.get('fecha')
    
    if not frontera_id: return redirect('modulo_liquidaciones')
        
    frontera = Frontera.objects.filter(id=frontera_id).first()
    contrato = Contrato.objects.filter(frontera_id=frontera_id).order_by('-fecha_inicio').first()
    
    context = {
        'frontera': frontera, 'contrato': contrato, 'fecha_str': fecha_str,
        'consumos_horarios': [], 'consumos_diarios': [], 'total_energia': Decimal('0.00'),
        'total_reactiva': Decimal('0.00'), 'componentes': {}, 'cu_variable': Decimal('0.00'),
        'total_a_facturar': Decimal('0.00'), 'chart_labels_json': '[]',
        'chart_data_activa_json': '[]', 'chart_data_reactiva_json': '[]', 'mes_nombre': "",
        'boxplot_data': '[]' 
    }

    if fecha_str:
        try:
            fecha_dt = datetime.strptime(fecha_str, '%Y-%m')
            fecha_periodo = fecha_dt.replace(day=1).date()
            context['mes_nombre'] = fecha_dt.strftime('%m/%Y')
            
            consumos_qs = ConsumoHorario.objects.filter(frontera=frontera, fecha__year=fecha_dt.year, fecha__month=fecha_dt.month)
            context['consumos_horarios'] = consumos_qs.order_by('fecha', 'hora')
            
            # --- BOX PLOT LOGIC ---
            boxplot_raw = [[] for _ in range(24)]
            for c in consumos_qs:
                if 0 <= c.hora - 1 < 24:
                    boxplot_raw[c.hora - 1].append(float(c.consumo_activo))
            
            boxplot_procesado = []
            for datos_hora in boxplot_raw:
                if datos_hora:
                    datos_hora.sort()
                    _min, _max, _median = min(datos_hora), max(datos_hora), statistics.median(datos_hora)
                    _q1 = statistics.median(datos_hora[:len(datos_hora)//2]) if datos_hora[:len(datos_hora)//2] else _min
                    _q3 = statistics.median(datos_hora[(len(datos_hora)+1)//2:]) if datos_hora[(len(datos_hora)+1)//2:] else _max
                    boxplot_procesado.append({'min': _min, 'q1': _q1, 'median': _median, 'q3': _q3, 'max': _max})
                else:
                    boxplot_procesado.append(None)
            
            context['boxplot_data'] = json.dumps(boxplot_procesado)

            # --- GRÁFICAS Y TOTALES ---
            diarios = consumos_qs.values('fecha').annotate(activa_dia=Sum('consumo_activo'), reactiva_dia=Sum('consumo_reactivo')).order_by('fecha')
            context['consumos_diarios'] = diarios
            context['chart_labels_json'] = json.dumps([d['fecha'].strftime('%d') for d in diarios])
            context['chart_data_activa_json'] = json.dumps([float(d['activa_dia']) for d in diarios])
            context['chart_data_reactiva_json'] = json.dumps([float(d['reactiva_dia']) for d in diarios])

            totales = consumos_qs.aggregate(a=Sum('consumo_activo'), r=Sum('consumo_reactivo'))
            context['total_energia'] = totales['a'] or Decimal('0.00')
            context['total_reactiva'] = totales['r'] or Decimal('0.00')
            
            # --- LIQUIDACIÓN (Usando el Helper) ---
            liq_datos = obtener_liquidacion_mes(frontera, fecha_periodo, context['total_energia'])
            context.update(liq_datos)

        except ValueError:
            pass

    return render(request, 'liquidaciones/detalle_consumo.html', context)

@login_required
def exportar_factura_pdf(request, frontera_id, fecha_str):
    frontera = get_object_or_404(Frontera, id=frontera_id)
    fecha_dt = datetime.strptime(fecha_str, '%Y-%m')
    fecha_periodo = fecha_dt.replace(day=1).date()
    
    consumos = ConsumoHorario.objects.filter(frontera=frontera, fecha__year=fecha_dt.year, fecha__month=fecha_dt.month)
    totales = consumos.aggregate(a=Sum('consumo_activo'), r=Sum('consumo_reactivo'))
    total_energia = totales['a'] or Decimal('0')
    total_reactiva = totales['r'] or Decimal('0')
    
    contrato = Contrato.objects.filter(frontera=frontera).order_by('-fecha_inicio').first()
    
    # --- LIQUIDACIÓN (Usando el Helper, ¡mira qué limpio quedó!) ---
    liq_datos = obtener_liquidacion_mes(frontera, fecha_periodo, total_energia)

    meses_es = {1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'}
    
    context = {
        'frontera': frontera,
        'contrato': contrato,
        'consumos': consumos,
        'total_energia': total_energia,
        'total_reactiva': total_reactiva,
        'componentes': liq_datos['componentes'],
        'cu_variable': liq_datos['cu_variable'],
        'total_a_facturar': liq_datos['total_a_facturar'],
        'mes_nombre': f"{meses_es[fecha_dt.month]} {fecha_dt.year}",
    }
    
    html_string = render_to_string('liquidaciones/factura_pdf.html', context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Factura_{frontera.numero_factura}.pdf"'
    
    HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf(response)
    return response
