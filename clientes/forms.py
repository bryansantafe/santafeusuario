# clientes/forms.py
from django import forms
from .models import Cliente, Frontera

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre_usuario', 'tipo_identificacion', 'numero_identificacion', 'telefono', 'correo_electronico', 'direccion_facturacion']

class FronteraForm(forms.ModelForm):
    class Meta:
        model = Frontera
        exclude = ['cliente'] ### Se excluey porque se asigna directamente en la vista