import json
from django.shortcuts import render, redirect
from django.db.models import Sum
from django.db import transaction
from decimal import Decimal
from datetime import datetime
from clientes.models import Cliente, Frontera
from .models import (
    Contrato, Periodo, ConsumoHorario,
    ComponenteG, ComponenteC, ComponenteD, ComponenteT, 
    ComponentePR, ComponenteR
)
import statistics # <-- Agrega esto junto a tus otros imports
from weasyprint import HTML
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required

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
                # 1. GUARDAR CONTRATO (Captura ipp_base e ipc_base)
                f_inicio = request.POST.get('fecha_inicio')
                defaults_contrato = {
                    'fecha_inicio': f_inicio,
                    'fecha_fin': request.POST.get('fecha_fin'),
                    'tipo_pld': request.POST.get('tipo_pld') or 'FIJO',
                    'precio_g_base': clean_decimal(request.POST.get('g_base')),
                    'precio_c_base': clean_decimal(request.POST.get('c_base')),
                    'ipp_base': clean_decimal(request.POST.get('ipp_base')), # Ya no será 1 por defecto si envías dato
                    'ipc_base': clean_decimal(request.POST.get('ipc_base')),
                }
                
                if c_id:
                    Contrato.objects.filter(id=c_id).update(**defaults_contrato)
                    contrato_guardado = Contrato.objects.get(id=c_id)
                else:
                    contrato_guardado = Contrato.objects.create(frontera=frontera, **defaults_contrato)

                # 2. GUARDAR COMPONENTES E INDEXAR SEGÚN TIPO
                if f_inicio:
                    fecha_dt = datetime.strptime(f_inicio, '%Y-%m-%d') 
                    periodo_obj, _ = Periodo.objects.get_or_create(fecha_mes=fecha_dt.replace(day=1).date())
                    
                    # --- LÓGICA DINÁMICA PARA G ---
                    g_tipo = request.POST.get('g_tipo_indice')
                    # Elegimos el denominador según el tipo de índice elegido
                    denominador_g = contrato_guardado.ipp_base if g_tipo == 'IPP' else contrato_guardado.ipc_base
                    numerador_g = periodo_obj.valor_ipp if g_tipo == 'IPP' else periodo_obj.valor_ipc
                    
                    g_indexado = contrato_guardado.precio_g_base * (numerador_g / denominador_g)

                    ComponenteG.objects.update_or_create(
                        contrato=contrato_guardado, periodo=periodo_obj, 
                        defaults={
                            'valor_base': contrato_guardado.precio_g_base, 
                            'tipo_indice': g_tipo,
                            'fecha_indice': request.POST.get('g_fecha_indice') or None,
                            'valor_indice': numerador_g,
                            'valor_indexado': g_indexado
                        }
                    )
                    
                    # --- LÓGICA DINÁMICA PARA C ---
                    c_tipo = request.POST.get('c_tipo_indice')
                    denominador_c = contrato_guardado.ipp_base if c_tipo == 'IPP' else contrato_guardado.ipc_base
                    numerador_c = periodo_obj.valor_ipp if c_tipo == 'IPP' else periodo_obj.valor_ipc

                    c_indexado = contrato_guardado.precio_c_base * (numerador_c / denominador_c)

                    ComponenteC.objects.update_or_create(
                        contrato=contrato_guardado, periodo=periodo_obj, 
                        defaults={
                            'valor_base': contrato_guardado.precio_c_base, 
                            'tipo_indice': c_tipo,
                            'fecha_indice': request.POST.get('c_fecha_indice') or None,
                            'valor_indice': numerador_c,
                            'valor_indexado': c_indexado
                        }
                    )

                return redirect(f"/liquidaciones/consumo/detalle/?frontera={frontera_id}&fecha={f_inicio[:7]}")
        except Exception as e:
            error_msj = f"Error al guardar: {str(e)}"

    # Cargar datos actuales para el formulario
    g_actual = ComponenteG.objects.filter(contrato=contrato).first() if contrato else None
    c_actual = ComponenteC.objects.filter(contrato=contrato).first() if contrato else None

    context = {
        'frontera': frontera, 
        'contrato': contrato,
        'g_actual': g_actual,
        'c_actual': c_actual,
        
        # Lógica de PLD
        'opciones_pld': [
            {'val': 'FIJO', 'active': bool(contrato and contrato.tipo_pld == 'FIJO')},
            {'val': 'BOLSA', 'active': bool(contrato and contrato.tipo_pld == 'BOLSA')},
            {'val': 'FORMULA', 'active': bool(contrato and contrato.tipo_pld == 'FORMULA')},
        ],
        
        # Lógica de Índice G
        'opciones_g': [
            {'val': 'IPP', 'active': bool(g_actual and g_actual.tipo_indice == 'IPP')},
            {'val': 'IPC', 'active': bool(g_actual and g_actual.tipo_indice == 'IPC')},
        ],
        
        # Lógica de Índice C
        'opciones_c': [
            {'val': 'IPP', 'active': bool(c_actual and c_actual.tipo_indice == 'IPP')},
            {'val': 'IPC', 'active': bool(c_actual and c_actual.tipo_indice == 'IPC')},
        ],
        'error_msj': error_msj,
    }
    return render(request, 'liquidaciones/gestionar_contrato.html', context)
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
        'boxplot_data': '[]' # <-- 1. Inicializa la variable aquí
    }

    if fecha_str:
        try:
            fecha_dt = datetime.strptime(fecha_str, '%Y-%m')
            fecha_periodo = fecha_dt.replace(day=1).date()
            context['mes_nombre'] = fecha_dt.strftime('%m/%Y')
            
            # 1. Obtener Consumos
            consumos_qs = ConsumoHorario.objects.filter(
                frontera=frontera, fecha__year=fecha_dt.year, fecha__month=fecha_dt.month
            )
            
            context['consumos_horarios'] = consumos_qs.order_by('fecha', 'hora')
            
            # --- NUEVA LÓGICA PARA EL BOX PLOT AQUÍ ---
# --- NUEVA LÓGICA PARA EL BOX PLOT AQUÍ ---
            boxplot_raw = [[] for _ in range(24)]
            for c in consumos_qs:
                indice_hora = c.hora - 1
                if 0 <= indice_hora < 24:
                    boxplot_raw[indice_hora].append(float(c.consumo_activo))
            
            boxplot_procesado = []
            for datos_hora in boxplot_raw:
                if len(datos_hora) > 0:
                    datos_hora.sort() # Ordenar de menor a mayor
                    n = len(datos_hora)
                    
                    # Cálculos estadísticos
                    _min = min(datos_hora)
                    _max = max(datos_hora)
                    _median = statistics.median(datos_hora)
                    
                    # Para Q1 y Q3 partimos la lista a la mitad
                    mitad_inf = datos_hora[:n//2]
                    mitad_sup = datos_hora[(n+1)//2:]
                    
                    _q1 = statistics.median(mitad_inf) if mitad_inf else _min
                    _q3 = statistics.median(mitad_sup) if mitad_sup else _max
                    
                    # Guardamos el formato exacto que pide Chart.js
                    boxplot_procesado.append({
                        'min': _min,
                        'q1': _q1,
                        'median': _median,
                        'q3': _q3,
                        'max': _max
                    })
                else:
                    boxplot_procesado.append(None) # Hora sin consumo
            
            context['boxplot_data'] = json.dumps(boxplot_procesado)
            # ------------------------------------------ # <-- 2. Asigna los datos al contexto
            # ------------------------------------------

            # Gráficas y Resumen Diario
            diarios = consumos_qs.values('fecha').annotate(
                activa_dia=Sum('consumo_activo'), reactiva_dia=Sum('consumo_reactivo')
            ).order_by('fecha')
            
            context['consumos_diarios'] = diarios
            context['chart_labels_json'] = json.dumps([d['fecha'].strftime('%d') for d in diarios])
            context['chart_data_activa_json'] = json.dumps([float(d['activa_dia']) for d in diarios])
            context['chart_data_reactiva_json'] = json.dumps([float(d['reactiva_dia']) for d in diarios])

            totales = consumos_qs.aggregate(a=Sum('consumo_activo'), r=Sum('consumo_reactivo'))
            context['total_energia'] = totales['a'] or Decimal('0.00')
            context['total_reactiva'] = totales['r'] or Decimal('0.00')
            
            # 2. LIQUIDACIÓN
            # Buscamos el periodo exacto o el más reciente anterior a la fecha
            periodo_m = Periodo.objects.filter(fecha_mes=fecha_periodo).first()
            if not periodo_m:
                periodo_m = Periodo.objects.filter(fecha_mes__lte=fecha_periodo).order_by('-fecha_mes').first()
            
            if contrato and periodo_m:
                # Buscamos G y C heredados o del mes
                g_obj = ComponenteG.objects.filter(contrato=contrato, periodo__fecha_mes__lte=fecha_periodo).order_by('-periodo__fecha_mes').first()
                c_obj = ComponenteC.objects.filter(contrato=contrato, periodo__fecha_mes__lte=fecha_periodo).order_by('-periodo__fecha_mes').first()
                
                # Buscamos componentes regulados por Operador y Periodo
                t = ComponenteT.objects.filter(periodo=periodo_m, operador_red=frontera.operador_red).first()
                r = ComponenteR.objects.filter(periodo=periodo_m, operador_red=frontera.operador_red).first()
                d = ComponenteD.objects.filter(periodo=periodo_m, operador_red=frontera.operador_red, nivel_tension=frontera.nivel_tension).first()
                pr = ComponentePR.objects.filter(periodo=periodo_m, operador_red=frontera.operador_red, nivel_tension=frontera.nivel_tension).first()

                # Asignamos valores
                context['componentes'] = {
                    'G (Generación)': g_obj.valor_indexado if g_obj else Decimal('0.00'),
                    'T (Transmisión)': t.valor if t else Decimal('0.00'),
                    'D (Distribución)': d.valor if d else Decimal('0.00'),
                    'PR (Pérdidas)': pr.valor if pr else Decimal('0.00'),
                    'R (Restricciones)': r.valor if r else Decimal('0.00'),
                    'C (Comercializ.)': c_obj.valor_indexado if c_obj else Decimal('0.00'),
                }
                context['cu_variable'] = sum(context['componentes'].values())
                context['total_a_facturar'] = context['total_energia'] * context['cu_variable']

        except ValueError:
            pass

    return render(request, 'liquidaciones/detalle_consumo.html', context)
@login_required
def detalle_frontera(request, frontera_id):
    frontera = get_object_or_404(Frontera, id=frontera_id)
    
    # Filtro de fechas (opcional)
    fecha_inicio = request.GET.get('inicio')
    fecha_fin = request.GET.get('fin')
    
    consumos = ConsumoHorario.objects.filter(frontera=frontera)
    
    if fecha_inicio and fecha_fin:
        consumos = consumos.filter(fecha__range=[fecha_inicio, fecha_fin])
    
    # --- LOGICA PARA GRAFICO DE LINEAS Y HEATMAP (Ya existente) ---
    labels_linea = [c.fecha.strftime('%d/%m') for c in consumos.order_by('fecha', 'hora')]
    datos_linea = [float(c.consumo_activo) for c in consumos.order_by('fecha', 'hora')]
    
    # --- NUEVA LOGICA: BOX PLOT HORARIO ---
    # Creamos una lista con 24 sublistas (una por cada hora del día) 
    boxplot_raw = [[] for _ in range(24)]
    
    for c in consumos:
        # Restamos 1 porque las horas van de 1-24 y los índices de lista de 0-23 
        indice_hora = c.hora - 1
        if 0 <= indice_hora < 24:
            boxplot_raw[indice_hora].append(float(c.consumo_activo))
    
    # Convertimos a JSON para pasarlo al template 
    boxplot_data_json = json.dumps(boxplot_raw)
    
    context = {
        'frontera': frontera,
        'consumos': consumos,
        'labels_linea': json.dumps(labels_linea),
        'datos_linea': json.dumps(datos_linea),
        'boxplot_data': boxplot_data_json, # Esta es la variable que usará el script del Box Plot 
    }
    
    return render(request, 'clientes/detalle_consumo.html', context)
@login_required
def exportar_factura_pdf(request, frontera_id, fecha_str):
    # 1. Obtener objetos base
    frontera = Frontera.objects.get(id=frontera_id)
    fecha_dt = datetime.strptime(fecha_str, '%Y-%m')
    
    # 2. Obtener Consumos y Totales (Agregamos la Reactiva)
    consumos = ConsumoHorario.objects.filter(
        frontera=frontera, 
        fecha__year=fecha_dt.year, 
        fecha__month=fecha_dt.month
    )
    
    totales = consumos.aggregate(a=Sum('consumo_activo'), r=Sum('consumo_reactivo'))
    total_energia = totales['a'] or Decimal('0')
    total_reactiva = totales['r'] or Decimal('0')
    
    # 3. Obtener Componentes CU (Costo Unitario)
    periodo = Periodo.objects.filter(fecha_mes=fecha_dt.replace(day=1)).first()
    contrato = Contrato.objects.filter(frontera=frontera).order_by('-fecha_inicio').first()
    
    comp_g = ComponenteG.objects.filter(contrato=contrato, periodo=periodo).first()
    valor_g = comp_g.valor_indexado if comp_g else Decimal('0')
    
    comp_c = ComponenteC.objects.filter(contrato=contrato, periodo=periodo).first()
    valor_c = comp_c.valor_indexado if comp_c else Decimal('0')
    
    comp_t = ComponenteT.objects.filter(periodo=periodo, operador_red=frontera.operador_red).first()
    valor_t = comp_t.valor if comp_t else Decimal('0')
    
    comp_d = ComponenteD.objects.filter(periodo=periodo, operador_red=frontera.operador_red, nivel_tension=frontera.nivel_tension).first()
    valor_d = comp_d.valor if comp_d else Decimal('0')
    
    comp_pr = ComponentePR.objects.filter(periodo=periodo, operador_red=frontera.operador_red, nivel_tension=frontera.nivel_tension).first()
    valor_pr = comp_pr.valor if comp_pr else Decimal('0')
    
    comp_r = ComponenteR.objects.filter(periodo=periodo, operador_red=frontera.operador_red).first()
    valor_r = comp_r.valor if comp_r else Decimal('0')
    
    # Armamos el diccionario de componentes exactamente como lo lee el HTML
    componentes = {
        'G (Generación)': valor_g,
        'T (Transmisión)': valor_t,
        'D (Distribución)': valor_d,
        'PR (Pérdidas)': valor_pr,
        'R (Restricciones)': valor_r,
        'C (Comercializ.)': valor_c,
    }
    
    cu_variable = sum(componentes.values())
    total_a_facturar = total_energia * cu_variable

    meses_es = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    mes_formateado = f"{meses_es[fecha_dt.month]} {fecha_dt.year}"

    # 4. Renderizado para PDF (Ajustamos los nombres del diccionario)
    context = {
        'frontera': frontera,
        'contrato': contrato,
        'consumos': consumos,
        'total_energia': total_energia,
        'total_reactiva': total_reactiva,
        'componentes': componentes,
        'cu_variable': cu_variable,
        'total_a_facturar': total_a_facturar,
        'mes_nombre': mes_formateado,
    }
    
    html_string = render_to_string('liquidaciones/factura_pdf.html', context)
    
    # 5. Generar PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Factura_{frontera.numero_factura}.pdf"'
    
    HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf(response)
    return response
###