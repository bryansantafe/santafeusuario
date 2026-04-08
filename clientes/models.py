from django.db import models
from django.contrib.auth.models import User


class Cliente(models.Model):
    TIPO_IDENTIFICACION_CHOICES = [
        ('CC', 'Cédula de Ciudadanía'),
        ('NIT', 'NIT (Número de Identificación Tributaria)'),
    ]
    nombre_usuario = models.CharField(max_length=255, verbose_name="Nombre del Usuario / Razón Social")
    tipo_identificacion = models.CharField(max_length=3, choices=TIPO_IDENTIFICACION_CHOICES, default='NIT')
    numero_identificacion = models.CharField(max_length=25, unique=True, verbose_name="Número de Identificación")
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")
    correo_electronico = models.EmailField(verbose_name="Correo Electrónico")
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
    # --- LISTA DE OPERADORES DE RED (Extraídos de tu imagen) ---
# --- LISTA DE OPERADORES DE RED (Extraídos del CSV resumen) ---
    # --- LISTA DE OPERADORES DE RED ---
    # Formato: ('Nombre exacto para cruzar con BD', 'Operador - Departamento')
    OPERADOR_CHOICES = [
        ('EPMD - EPM Mercado de Comercialización - ANTIOQUIA', 'EPM - ANTIOQUIA'),
        ('ENID - ENELAR Mercado de Comercialización - ARAUCA', 'ENELAR - ARAUCA'),
        ('EBPD - BAJO PUTUMAYO  Mercado de Comercialización - BAJO PUTUMAYO', 'EBP - BAJO PUTUMAYO'),
        ('ENDD - ENEL Mercado de Comercialización - BOGOTA - CUNDINAMARCA', 'ENEL - BOGOTÁ'),
        ('EBSD - EBSA Mercado de Comercialización - BOYACA', 'EBSA - BOYACÁ'),
        ('CHCD - CHEC S.A. E.S.P. BIC Mercado de Comercialización - CALDAS', 'CHEC - CALDAS'),
        ('EMID - EMCALI Mercado de Comercialización - CALI - YUMBO - PUERTO TEJADA', 'EMCALI - CALI'),
        ('CQTD - ELECTROCAQUETA Mercado de Comercialización - CAQUETA', 'ELECTROCAQUETA - CAQUETÁ'),
        ('CMMD - CARIBEMAR Mercado de Comercialización - CARIBE MAR', 'AFINIA - CARIBE MAR'),
        ('CSID - AIR-E Mercado de Comercialización - CARIBE SOL', 'AIRE - CARIBE SOL'),
        ('EEPD - EEP Mercado de Comercialización - CARTAGO', 'EMCARTAGO - CARTAGO'),
        ('CASD - ENERCA Mercado de Comercialización - CASANARE', 'ENERCA - CASANARE'),
        ('CEOD - CEO S.A.S E.S.P. Mercado de Comercialización - CAUCA', 'CEO - CAUCA'),
        ('EDPD - DISPAC S.A. E.S.P. Mercado de Comercialización - CHOCO', 'DISPAC - CHOCÓ'),
        ('EGVD - ENERGUAVIARE Mercado de Comercialización - GUAVIARE', 'ENERGUAVIARE - GUAVIARE'),
        ('HLAD - ELECTROHUILA Mercado de Comercialización - HUILA', 'ELECTROHUILA - HUILA'),
        ('EMSD - EMSA Mercado de Comercialización - META', 'EMSA - META'),
        ('CDND - CEDENAR Mercado de Comercialización - NARIÑO', 'CEDENAR - NARIÑO'),
        ('CNSD - CENS Mercado de Comercialización - NORTE DE SANTANDER', 'CENS - NORTE DE SANTANDER'),
        ('EEPD - EEP Mercado de Comercialización - PEREIRA', 'EEP - PEREIRA'),
        ('EMED - EMEE Mercado de Comercialización - POPAYAN - PURACE', 'EMEE - POPAYÁN'),
        ('EPTD - PUTUMAYO Mercado de Comercialización - PUTUMAYO', 'EPT - PUTUMAYO'),
        ('EDQD - EDEQ Mercado de Comercialización - QUINDIO', 'EDEQ - QUINDÍO'),
        ('RTQD - RUITOQUE Mercado de Comercialización - RUITOQUE', 'RUITOQUE - RUITOQUE'),
        ('ESSD - ESSA Mercado de Comercialización - SANTANDER', 'ESSA - SANTANDER'),
        ('EPSD - CELSIA COLOMBIA Mercado de Comercialización - TOLIMA', 'CELSIA - TOLIMA'),
        ('CETD - CETSA Mercado de Comercialización - TULUA', 'CETSA - TULUÁ'),
        ('EPSD - CELSIA COLOMBIA Mercado de Comercialización - VALLE DEL CAUCA', 'CELSIA - VALLE DEL CAUCA'),
    ]

    # --- LISTA DE DEPARTAMENTOS DE COLOMBIA ---
    DEPARTAMENTO_CHOICES = [
        ('AMAZONAS', 'Amazonas'), ('ANTIOQUIA', 'Antioquia'), ('ARAUCA', 'Arauca'),
        ('ATLANTICO', 'Atlántico'), ('BOGOTA', 'Bogotá D.C.'), ('BOLIVAR', 'Bolívar'),
        ('BOYACA', 'Boyacá'), ('CALDAS', 'Caldas'), ('CAQUETA', 'Caquetá'),
        ('CASANARE', 'Casanare'), ('CAUCA', 'Cauca'), ('CESAR', 'Cesar'),
        ('CHOCO', 'Chocó'), ('CORDOBA', 'Córdoba'), ('CUNDINAMARCA', 'Cundinamarca'),
        ('GUAINIA', 'Guainía'), ('GUAVIARE', 'Guaviare'), ('HUILA', 'Huila'),
        ('GUAJIRA', 'La Guajira'), ('MAGDALENA', 'Magdalena'), ('META', 'Meta'),
        ('NARINO', 'Nariño'), ('NORTE_SANTANDER', 'Norte de Santander'), ('PUTUMAYO', 'Putumayo'),
        ('QUINDIO', 'Quindío'), ('RISARALDA', 'Risaralda'), ('SAN_ANDRES', 'San Andrés'),
        ('SANTANDER', 'Santander'), ('SUCRE', 'Sucre'), ('TOLIMA', 'Tolima'),
        ('VALLE_CAUCA', 'Valle del Cauca'), ('VAUPES', 'Vaupés'), ('VICHADA', 'Vichada'),
    ]

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