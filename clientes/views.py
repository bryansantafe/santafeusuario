### clientes.views.py


from django.shortcuts import render, redirect, get_object_or_404, redirect
from .models import Cliente, Frontera, AceptacionTerminos
from django.utils import timezone
from django.contrib.auth.decorators import login_required

@login_required
def aceptar_terminos(request):
    if hasattr(request.user, 'registro_terminos'):
        return redirect('dashboard')

    if request.method == 'POST':
        AceptacionTerminos.objects.create(
            user=request.user,
            nombre_usuario=request.user.username,
            correo_asociado=request.user.email
        )
        return redirect('dashboard')

    return render(request, 'clientes/aceptar_terminos.html')


@login_required
def lista_clientes(request):
    # Traemos todos los clientes de la base de datos
    clientes = Cliente.objects.all().order_by('-fecha_register')
    return render(request, 'clientes/lista.html', {'clientes': clientes})
@login_required
def detalle_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    fronteras = cliente.fronteras.all()

    if request.method == 'POST':
        # --- 1. PRIORIDAD: ELIMINAR CLIENTE ---
        # Si el usuario hizo clic en eliminar, lo sacamos del sistema de inmediato
        if 'btn_eliminar_cliente' in request.POST:
            cliente.delete()
            return redirect('lista_clientes')

        # --- 2. PRIORIDAD: ELIMINAR FRONTERA ---
        elif 'btn_eliminar_frontera' in request.POST:
            frontera_id = request.POST.get('frontera_id')
            frontera = get_object_or_404(Frontera, id=frontera_id)
            frontera.delete()
            return redirect('detalle_cliente', cliente_id=cliente.id)

        # --- 3. ACTUALIZAR CLIENTE ---
        elif 'btn_actualizar_cliente' in request.POST:
            
            cliente.telefono = request.POST.get('telefono')
            cliente.correo_electronico = request.POST.get('correo_electronico') # Asegúrate de tener este campo en models.py
            cliente.direccion_facturacion = request.POST.get('direccion_facturacion')
    
            cliente.save() # Guardamos los cambios
            return redirect('detalle_cliente', cliente_id=cliente.id)

        # --- 4. AGREGAR FRONTERA ---
        elif 'btn_agregar_frontera' in request.POST:
            Frontera.objects.create(
                cliente=cliente,
                numero_contrato=request.POST.get('numero_contrato'),
                numero_medidor=request.POST.get('numero_medidor'),
                numero_factura=request.POST.get('numero_factura'),
                comercializador=request.POST.get('comercializador'),
                operador_red=request.POST.get('operador_red'),
                mercado=request.POST.get('mercado'),
                nivel_tension=request.POST.get('nivel_tension'),
                departamento=request.POST.get('departamento'),
                municipio_frontera=request.POST.get('municipio_frontera'),
                direccion_frontera=request.POST.get('direccion_frontera'),
            )
            return redirect('detalle_cliente', cliente_id=cliente.id)

    return render(request, 'clientes/detalle.html', {
        'cliente': cliente,
        'fronteras': fronteras,
        'operadores': Frontera.OPERADOR_CHOICES,
        'departamentos': Frontera.DEPARTAMENTO_CHOICES,
    })

# 3. CREAR CLIENTE (Actualizado con tus campos reales)
@login_required
def crear_cliente(request):
    if request.method == 'POST':
        # Capturamos los datos del formulario (deben coincidir con el 'name' de tus <input>)
        nombre = request.POST.get('nombre_usuario')
        tipo_id = request.POST.get('tipo_identificacion')
        num_id = request.POST.get('numero_identificacion')
        tel = request.POST.get('telefono')
        dir_fact = request.POST.get('direccion_facturacion')
        correo = request.POST.get('correo_electronico')

        # Creamos el registro en PostgreSQL
        Cliente.objects.create(
            user=request.user, 
            nombre_usuario=nombre,
            tipo_identificacion=tipo_id,
            numero_identificacion=num_id,
            telefono=tel,
            direccion_facturacion=dir_fact,
            correo_electronico=correo,
        )
        return redirect('lista_clientes')
    
    # Si es un GET, simplemente mostramos el formulario vacío
    return render(request, 'clientes/formulario_cliente.html')