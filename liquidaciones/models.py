from django.db import models
# Importamos Frontera desde tu otra app de clientes
from clientes.models import Frontera 

class Periodo(models.Model):
    """
    Representa un mes calendario. Aquí se centralizan los índices 
    económicos nacionales (IPC, IPP) para que no tengas que repetirlos.
    """
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
    """
    Contrato comercial con el cliente. Contiene los precios base 
    y los índices de referencia al momento de la firma.
    """
    frontera = models.ForeignKey(Frontera, on_delete=models.CASCADE, related_name='contratos')
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    tipo_pld = models.CharField(max_length=20, default='FIJO') # FIJO, BOLSA, FORMULA
    
    # Valores base para el cálculo de indexación futura
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
    # Mantenemos estos campos porque tu view gestionar_contrato los usa
    tipo_indice = models.CharField(max_length=10, null=True, blank=True) # IPC o IPP
    fecha_indice = models.DateField(null=True, blank=True)
    valor_indice = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    # Resultado de la fórmula: Base * (Indice Mes / Indice Contrato)
    valor_indexado = models.DecimalField(max_digits=12, decimal_places=4, default=0)

class ComponenteC(models.Model):
    contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE)
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE)
    valor_base = models.DecimalField(max_digits=12, decimal_places=4)
    tipo_indice = models.CharField(max_length=10, null=True, blank=True)
    fecha_indice = models.DateField(null=True, blank=True)
    valor_indice = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    valor_indexado = models.DecimalField(max_digits=12, decimal_places=4, default=0)

# COMPONENTES REGULADOS: Dependen del Periodo Y del Operador de Red
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

class ConsumoHorario(models.Model):
    frontera = models.ForeignKey(Frontera, on_delete=models.CASCADE)
    fecha = models.DateField()
    hora = models.IntegerField() # 1 a 24
    consumo_activo = models.DecimalField(max_digits=12, decimal_places=4)
    consumo_reactivo = models.DecimalField(max_digits=12, decimal_places=4)
    es_estimado = models.BooleanField(default=False)

    class Meta:
        # Indexamos para que las gráficas y tablas carguen instantáneamente
        indexes = [
            models.Index(fields=['frontera', 'fecha']),
        ]