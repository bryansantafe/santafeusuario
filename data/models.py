from django.db import models

# --- ENTIDADES PRINCIPALES ---

class Agente(models.Model):
    agente_id = models.CharField("Código SIC", max_length=50, primary_key=True)
    nombre_agente = models.CharField(max_length=255)
    actividad = models.CharField(max_length=100) # Generador, Comercializador, etc.
    clasificacion = models.CharField(max_length=100)
    estado = models.CharField(max_length=50)
    fecha_registro = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.agente_id} - {self.nombre_agente}"

class Recurso(models.Model):
    recurso_id = models.CharField(max_length=50, primary_key=True)
    agente = models.ForeignKey(Agente, on_delete=models.CASCADE, related_name='recursos')
    nombre_recurso = models.CharField(max_length=255)
    capacidad_efectiva_neta = models.DecimalField(max_digits=12, decimal_places=4)
    tipo_tecnologia = models.CharField(max_length=100)
    
    # --- NUEVOS CAMPOS ---
    fecha_operacion = models.DateField(null=True, blank=True)
    municipio = models.CharField(max_length=100, null=True, blank=True)
    departamento = models.CharField(max_length=100, null=True, blank=True)
    combustible = models.CharField(max_length=100, null=True, blank=True)
    estado_recurso = models.CharField(max_length=100, null=True, blank=True)
    clasificacion = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.nombre_recurso} ({self.tipo_tecnologia})"

# --- MÉTRICAS DE MERCADO (PRECIOS Y BALANCE) ---

class MetricasMercadoPrecios(models.Model):
    fecha_operacion = models.DateField()
    periodo_hora = models.PositiveIntegerField()
    precio_bolsa_nacional = models.DecimalField(max_digits=18, decimal_places=4)
    precio_escasez_activacion   = models.DecimalField(max_digits=18, decimal_places=4)
    precio_marginal_escasez = models.DecimalField(max_digits=18, decimal_places=4)
    precio_escasez_ponderado = models.DecimalField(max_digits=18, decimal_places=4)
    costo_equivalente_real_energia = models.DecimalField(max_digits=18, decimal_places=4)
    trm_dia = models.DecimalField(max_digits=12, decimal_places=2)
    fuente_archivo = models.CharField(max_length=255)

    class Meta:
        unique_together = ('fecha_operacion', 'periodo_hora')
        verbose_name_plural = "Métricas Mercado Precios"

class MetricasDemandaBalance(models.Model):
    agente = models.ForeignKey(Agente, on_delete=models.CASCADE)
    fecha_operacion = models.DateField()
    demanda_no_regulada = models.DecimalField(max_digits=18, decimal_places=4)
    demanda_regulada = models.DecimalField(max_digits=18, decimal_places=4)
    perdidas_no_regulada = models.DecimalField(max_digits=18, decimal_places=4)
    perdidas_regulada = models.DecimalField(max_digits=18, decimal_places=4)
    demanda_no_cubierta = models.DecimalField(max_digits=18, decimal_places=4)
    factor_ajuste_o_e_f = models.DecimalField(max_digits=10, decimal_places=6)
    fuente_archivo = models.CharField(max_length=255)

# --- MÉTRICAS DE LIQUIDACIÓN Y CONTRATOS ---

class MetricasTransaccionesLiquidacion(models.Model):
    agente = models.ForeignKey(Agente, on_delete=models.CASCADE)
    fecha_operacion = models.DateField()
    compras_bolsa_cop = models.DecimalField(max_digits=20, decimal_places=2)
    ventas_bolsa_cop = models.DecimalField(max_digits=20, decimal_places=2)
    compras_reconciliacion_cop = models.DecimalField(max_digits=20, decimal_places=2)
    ventas_reconciliacion_cop = models.DecimalField(max_digits=20, decimal_places=2)
    responsabilidad_agc_cop = models.DecimalField(max_digits=20, decimal_places=2)
    servicios_sic_cnd_cop = models.DecimalField(max_digits=20, decimal_places=2)
    neto_cargo_confiabilidad_cop = models.DecimalField(max_digits=20, decimal_places=2)
    valor_srpf_cop = models.DecimalField(max_digits=20, decimal_places=2)
    fuente_archivo = models.CharField(max_length=255)

class MetricasContratosPrivados(models.Model):
    contrato_id = models.CharField(max_length=100, primary_key=True)
    agente = models.ForeignKey(Agente, on_delete=models.CASCADE)
    contraparte_id = models.CharField(max_length=50)
    fecha_operacion = models.DateField()
    periodo_hora = models.PositiveIntegerField()
    cantidad_despachada_kwh = models.DecimalField(max_digits=18, decimal_places=4)
    tarifa_contrato_cop = models.DecimalField(max_digits=12, decimal_places=2)
    tipo_despacho_pc_pd = models.CharField(max_length=10) # PC o PD
    mercado_r_nr = models.CharField(max_length=10) # R o NR
    fuente_archivo = models.CharField(max_length=255)

# --- MÉTRICAS TÉCNICAS Y OPERATIVAS ---

class MetricasGeneracionCapacidad(models.Model):
    recurso = models.ForeignKey(Recurso, on_delete=models.CASCADE)
    fecha_operacion = models.DateField()
    periodo_hora = models.PositiveIntegerField()
    generacion_real = models.DecimalField(max_digits=18, decimal_places=4)
    generacion_ideal = models.DecimalField(max_digits=18, decimal_places=4)
    generacion_seguridad = models.DecimalField(max_digits=18, decimal_places=4)
    disponibilidad_comercial = models.DecimalField(max_digits=18, decimal_places=4)
    disponibilidad_real = models.DecimalField(max_digits=18, decimal_places=4)
    causa_restriccion = models.TextField(null=True, blank=True)
    fuente_archivo = models.CharField(max_length=255)

class MetricasConfiabilidadSeguridad(models.Model):
    recurso = models.ForeignKey(Recurso, on_delete=models.CASCADE)
    fecha_operacion = models.DateField()
    oef_diaria = models.DecimalField(max_digits=18, decimal_places=4)
    precio_cargo_confiabilidad = models.DecimalField(max_digits=18, decimal_places=4)
    remuneracion_real_individual = models.DecimalField(max_digits=20, decimal_places=2)
    desviacion_oef_ajustada = models.DecimalField(max_digits=18, decimal_places=4)
    flag_activacion_escasez = models.BooleanField(default=False)
    fuente_archivo = models.CharField(max_length=255)

class MetricasIntercambiosHidrologia(models.Model):
    id_contexto = models.AutoField(primary_key=True)
    enlace_id = models.CharField(max_length=50) # TIEs u otros
    fecha_operacion = models.DateField()
    energia_exportada_tie = models.DecimalField(max_digits=18, decimal_places=4)
    energia_importada_tie = models.DecimalField(max_digits=18, decimal_places=4)
    nivel_embalses_porcentaje = models.DecimalField(max_digits=5, decimal_places=2)
    nivel_enficc_probabilistico = models.DecimalField(max_digits=5, decimal_places=2)
    energia_remanente_diaria = models.DecimalField(max_digits=18, decimal_places=4)
    demanda_desconectable_verificada = models.DecimalField(max_digits=18, decimal_places=4)
    fuente_archivo = models.CharField(max_length=255)
