from django.db import models
from django.contrib.auth.models import User
from .choices import OPERADOR_CHOICES, DEPARTAMENTO_CHOICES 

class Cliente(models.Model):
    # user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_cliente')
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_cliente', null=True, blank=True)
    
    TIPO_IDENTIFICACION_CHOICES = [
        ('CC', 'Cédula de Ciudadanía'),
        ('NIT', 'NIT (Número de Identificación Tributaria)'),
    ]
    nombre_usuario = models.CharField(max_length=255, verbose_name="Nombre del Usuario / Razón Social")
    tipo_identificacion = models.CharField(max_length=3, choices=TIPO_IDENTIFICACION_CHOICES, default='NIT')
    numero_identificacion = models.CharField(max_length=25, unique=True, verbose_name="Número de Identificación")
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")
    correo_electronico = models.EmailField(unique=True, verbose_name="Correo Electrónico") 
    direccion_facturacion = models.TextField(verbose_name="Dirección de Facturación")
    fecha_register = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre_usuario

    @property
    def es_nit(self):
        return self.tipo_identificacion == 'NIT'

    @property
    def es_cc(self):
        return self.tipo_identificacion == 'CC'

class Frontera(models.Model):

    MERCADO_CHOICES = [('R', 'Regulado'), ('NR', 'No Regulado')]
    TENSION_CHOICES = [
        (1, '1'), 
        (2, '2'), 
        (3, '3'), 
        (4, '4')
    ]

    # Relaciones y campos
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='fronteras')
    numero_contrato = models.CharField(max_length=50)
    numero_factura = models.CharField(max_length=50)
    frontera_sic = models.CharField(max_length=50)
    numero_medidor = models.CharField(max_length=50)
    comercializador = models.CharField(max_length=150)
    
    # Campos con las nuevas opciones
    operador_red = models.CharField(max_length=255, choices=OPERADOR_CHOICES)
    departamento = models.CharField(max_length=50, choices=DEPARTAMENTO_CHOICES)
    
    # El municipio lo dejamos como texto para no saturar el código
    municipio_frontera = models.CharField(max_length=100, verbose_name="Municipio")
    
    mercado = models.CharField(max_length=2, choices=MERCADO_CHOICES)
    nivel_tension = models.IntegerField(choices=TENSION_CHOICES)
    direccion_frontera = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.numero_contrato} - {self.operador_red}"

class AceptacionTerminos(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='registro_terminos')
    
    nombre_usuario = models.CharField(max_length=255, verbose_name="Usuario que aceptó")
    correo_asociado = models.EmailField(verbose_name="Correo en el momento de aceptación")
    fecha_aceptacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y hora")

    def __str__(self):
        return f"{self.nombre_usuario} - Aceptó: {self.fecha_aceptacion.strftime('%Y-%m-%d %H:%M')}"