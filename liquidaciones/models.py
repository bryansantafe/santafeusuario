from django.db import models
from clientes.models import Frontera 

class Periodo(models.Model):
    fecha_mes = models.DateField(unique=True, verbose_name="Mes/Año (Día 1)")
    valor_ipc = models.DecimalField(max_digits=12, decimal_places=4, default=0, verbose_name="IPC del Mes")
    valor_ipp = models.DecimalField(max_digits=12, decimal_places=4, default=0, verbose_name="IPP del Mes")

    class Meta:
        verbose_name = "Periodo e Índices"
        verbose_name_plural = "Periodos e Índices"
        ordering = ['-fecha_mes']

    def __str__(self):
        return self.fecha_mes.strftime('%m/%Y')

class Contrato(models.Model):
    frontera = models.ForeignKey(Frontera, on_delete=models.CASCADE, related_name='contratos')
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    tipo_pld = models.CharField(max_length=20, default='FIJO')
    
    precio_g_base = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    precio_c_base = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    ipp_base = models.DecimalField(max_digits=12, decimal_places=4, default=1.0)
    ipc_base = models.DecimalField(max_digits=12, decimal_places=4, default=1.0)

    def __str__(self):
        return f"Contrato {self.frontera.numero_factura} ({self.fecha_inicio})"

class ComponenteG(models.Model):
    contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE)
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE)
    valor_base = models.DecimalField(max_digits=12, decimal_places=4)
    tipo_indice = models.CharField(max_length=10, null=True, blank=True) 
    fecha_indice = models.DateField(null=True, blank=True)
    valor_indice = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    valor_indexado = models.DecimalField(max_digits=12, decimal_places=4, default=0)

    def save(self, *args, **kwargs):
        if self.tipo_indice and self.periodo and self.contrato:
            numerador = self.periodo.valor_ipp if self.tipo_indice == 'IPP' else self.periodo.valor_ipc
            denominador = self.contrato.ipp_base if self.tipo_indice == 'IPP' else self.contrato.ipc_base
            
            if denominador != 0:
                self.valor_indice = numerador
                self.valor_indexado = self.valor_base * (numerador / denominador)
        super().save(*args, **kwargs)

class ComponenteC(models.Model):
    contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE)
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE)
    valor_base = models.DecimalField(max_digits=12, decimal_places=4)
    tipo_indice = models.CharField(max_length=10, null=True, blank=True)
    fecha_indice = models.DateField(null=True, blank=True)
    valor_indice = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    valor_indexado = models.DecimalField(max_digits=12, decimal_places=4, default=0)

    def save(self, *args, **kwargs):
        if self.tipo_indice and self.periodo and self.contrato:
            numerador = self.periodo.valor_ipp if self.tipo_indice == 'IPP' else self.periodo.valor_ipc
            denominador = self.contrato.ipp_base if self.tipo_indice == 'IPP' else self.contrato.ipc_base
            
            if denominador != 0:
                self.valor_indice = numerador
                self.valor_indexado = self.valor_base * (numerador / denominador)
        super().save(*args, **kwargs)


# --- COMPONENTES RESTAURADOS ---

class ComponenteD(models.Model):
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE)
    operador_red = models.CharField(max_length=100)
    nivel_tension = models.IntegerField()
    valor = models.DecimalField(max_digits=12, decimal_places=4)

class ComponentePR(models.Model):
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE)
    operador_red = models.CharField(max_length=100)
    nivel_tension = models.IntegerField()
    valor = models.DecimalField(max_digits=12, decimal_places=4)

class ComponenteT(models.Model):
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE)
    operador_red = models.CharField(max_length=100)
    valor = models.DecimalField(max_digits=12, decimal_places=4)

class ComponenteR(models.Model):
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE)
    operador_red = models.CharField(max_length=100)
    valor = models.DecimalField(max_digits=12, decimal_places=4)


# --- CONSUMOS ---

class ConsumoHorario(models.Model):
    frontera = models.ForeignKey(Frontera, on_delete=models.CASCADE)
    fecha = models.DateField()
    hora = models.IntegerField() 
    consumo_activo = models.DecimalField(max_digits=12, decimal_places=4)
    consumo_reactivo = models.DecimalField(max_digits=12, decimal_places=4)
    es_estimado = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['frontera', 'fecha']),
        ]