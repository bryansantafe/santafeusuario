### clientes.views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db import transaction
from django.contrib import messages

from .models import Cliente, Frontera, AceptacionTerminos
from .forms import ClienteForm, FronteraForm

def es_staff(user):
    return user.is_staff

@login_required
def aceptar_terminos(request):
    if hasattr(request.user, 'registro_terminos'):
        return redirect('core:dashboard')

    if request.method == 'POST':
        AceptacionTerminos.objects.create(
            user=request.user,
            nombre_usuario=request.user.username,
            correo_asociado=request.user.email
        )
        return redirect('core:dashboard')

    return render(request, 'clientes/aceptar_terminos.html')


@login_required
@user_passes_test(es_staff, login_url='/reportes/')
def lista_clientes(request):
    clientes = Cliente.objects.all().order_by('-fecha_register')
    return render(request, 'clientes/lista.html', {'clientes': clientes})


@login_required
@user_passes_test(es_staff, login_url='/reportes/')
def detalle_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    fronteras = cliente.fronteras.all()

    if request.method == 'POST':
        # 1. ELIMINAR CLIENTE
        if 'btn_eliminar_cliente' in request.POST:
            cliente.delete()
            messages.success(request, "Cliente eliminado correctamente.")
            return redirect('clientes:lista_clientes')

        # 2. ELIMINAR FRONTERA
        elif 'btn_eliminar_frontera' in request.POST:
            frontera_id = request.POST.get('frontera_id')
            frontera = get_object_or_404(Frontera, id=frontera_id, cliente=cliente) # Verificación de seguridad
            frontera.delete()
            messages.success(request, "Frontera eliminada.")
            return redirect('clientes:detalle_cliente', cliente_id=cliente.id)

        # 3. ACTUALIZAR CLIENTE (Usando el form instanciado)
        elif 'btn_actualizar_cliente' in request.POST:
            form_cliente = ClienteForm(request.POST, instance=cliente)
            if form_cliente.is_valid():
                form_cliente.save()
                messages.success(request, "Datos del cliente actualizados.")
            return redirect('clientes:detalle_cliente', cliente_id=cliente.id)

        # 4. AGREGAR FRONTERA (Dejamos que el form valide todo)
        elif 'btn_agregar_frontera' in request.POST:
            form_frontera = FronteraForm(request.POST)
            if form_frontera.is_valid():
                nueva_frontera = form_frontera.save(commit=False)
                nueva_frontera.cliente = cliente
                nueva_frontera.save()
                messages.success(request, "Nueva frontera agregada.")
            else:
                messages.error(request, "Error al agregar la frontera. Revisa los datos.")
            return redirect('clientes:detalle_cliente', cliente_id=cliente.id)

    # Si es GET, pasamos formularios vacíos para usarlos en el HTML
    contexto = {
        'cliente': cliente,
        'fronteras': fronteras,
        'form_cliente': ClienteForm(instance=cliente), # Pre-llena los datos para actualizar
        'form_frontera': FronteraForm(), # Formulario vacío para crear
    }
    return render(request, 'clientes/detalle.html', contexto)

# 3. CREAR CLIENTE (Actualizado con tus campos reales)

@login_required
@user_passes_test(es_staff, login_url='/reportes/')
def crear_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        
        if form.is_valid():
            correo = form.cleaned_data['correo_electronico']
            num_identificacion = form.cleaned_data['numero_identificacion']
            nombre = form.cleaned_data['nombre_usuario']

            
            if User.objects.filter(username=correo).exists(): ## Validar que el correo no exista ya como User en Django
                messages.error(request, "Este correo ya está asociado a una cuenta de acceso.")
                return render(request, 'clientes/formulario_cliente.html', {'form': form})

            try:
                with transaction.atomic(): ## Esto garantiza que si algo falla, no se guarde NADA
                    user = User.objects.create_user(
                        username=correo, 
                        email=correo, 
                        password=num_identificacion,
                        first_name=nombre[:30] # Django first_name tiene max_length=30
                    )

                    user.is_staff = False
                    user.is_superuser = False
                    user.save()
                    
                    cliente = form.save(commit=False) ## Se guarda el cliente vinculándolo al usuario
                    cliente.user = user
                    cliente.save()

                messages.success(request, "Cliente y credenciales de acceso creadas con éxito.")
                return redirect('clientes:lista_clientes')
            
            except Exception as e:
                messages.error(request, f"Ocurrió un error interno: {str(e)}")
        else:
            messages.error(request, "Por favor, corrige los errores del formulario.")
    else:
        form = ClienteForm()
    
    return render(request, 'clientes/formulario_cliente.html', {'form': form})