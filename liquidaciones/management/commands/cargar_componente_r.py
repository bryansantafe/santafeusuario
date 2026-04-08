import csv
from decimal import Decimal
from datetime import datetime
from django.core.management.base import BaseCommand

# Asegúrate de usar el nombre correcto de tu app
from liquidaciones.models import ComponenteR, Periodo 

class Command(BaseCommand):
    help = 'Carga los datos desde un archivo CSV para el Componente R (Restricciones)'

    def add_arguments(self, parser):
        parser.add_argument('ruta_csv', type=str, help='Ruta absoluta al archivo CSV')
        parser.add_argument('fecha_periodo', type=str, help='Fecha del periodo en formato MM/YYYY (ej: 01/2026)')

    def handle(self, *args, **kwargs):
        ruta_csv = kwargs['ruta_csv']
        fecha_periodo_str = kwargs['fecha_periodo']

        MAPEO_CORTO_A_LARGO = {
            'CEDENAR - NARIÑO': 'CDND - CEDENAR Mercado de Comercialización - NARIÑO',
            'CELSIA COLOMBIA - VALLE DEL CAUCA': 'EPSD - CELSIA COLOMBIA Mercado de Comercialización - VALLE DEL CAUCA',
            'CEO S.A.S E.S.P. - CAUCA': 'CEOD - CEO S.A.S E.S.P. Mercado de Comercialización - CAUCA',
            'CETSA - TULUA': 'CETD - CETSA Mercado de Comercialización - TULUA',
            'EEP - CARTAGO': 'EEPD - EEP Mercado de Comercialización - CARTAGO',
            'EMCALI - CALI - YUMBO - PUERTO TEJADA': 'EMID - EMCALI Mercado de Comercialización - CALI - YUMBO - PUERTO TEJADA',
            'EMEE - POPAYAN - PURACE': 'EMED - EMEE Mercado de Comercialización - POPAYAN - PURACE',
            'CELSIA COLOMBIA - TOLIMA': 'EPSD - CELSIA COLOMBIA Mercado de Comercialización - TOLIMA',
            'EBSA - BOYACA': 'EBSD - EBSA Mercado de Comercialización - BOYACA',
            'ELECTROHUILA - HUILA': 'HLAD - ELECTROHUILA Mercado de Comercialización - HUILA',
            'ENEL - BOGOTA - CUNDINAMARCA': 'ENDD - ENEL Mercado de Comercialización - BOGOTA - CUNDINAMARCA',
            'ENELAR - ARAUCA': 'ENID - ENELAR Mercado de Comercialización - ARAUCA',
            'CENS - NORTE DE SANTANDER': 'CNSD - CENS Mercado de Comercialización - NORTE DE SANTANDER',
            'CHEC S.A. E.S.P. BIC - CALDAS': 'CHCD - CHEC S.A. E.S.P. BIC Mercado de Comercialización - CALDAS',
            'EDEQ - QUINDIO': 'EDQD - EDEQ Mercado de Comercialización - QUINDIO',
            'EEP - PEREIRA': 'EEPD - EEP Mercado de Comercialización - PEREIRA',
            'EPM - ANTIOQUIA': 'EPMD - EPM Mercado de Comercialización - ANTIOQUIA',
            'ESSA - SANTANDER': 'ESSD - ESSA Mercado de Comercialización - SANTANDER',
            'RUITOQUE - RUITOQUE': 'RTQD - RUITOQUE Mercado de Comercialización - RUITOQUE',
            'BAJO PUTUMAYO  - BAJO PUTUMAYO': 'EBPD - BAJO PUTUMAYO  Mercado de Comercialización - BAJO PUTUMAYO',
            'ELECTROCAQUETA - CAQUETA': 'CQTD - ELECTROCAQUETA Mercado de Comercialización - CAQUETA',
            'EMSA - META': 'EMSD - EMSA Mercado de Comercialización - META',
            'ENERCA - CASANARE': 'CASD - ENERCA Mercado de Comercialización - CASANARE',
            'PUTUMAYO - PUTUMAYO': 'EPTD - PUTUMAYO Mercado de Comercialización - PUTUMAYO',
        }

        try:
            fecha_obj = datetime.strptime(fecha_periodo_str, '%m/%Y').replace(day=1).date()
            periodo = Periodo.objects.get(fecha_mes=fecha_obj)
            self.stdout.write(self.style.SUCCESS(f"✅ Periodo encontrado: {periodo}"))
        except Periodo.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"❌ Error: El periodo {fecha_periodo_str} no existe en la BD."))
            return

        registros_creados = 0
        registros_actualizados = 0

        try:
            # Usamos punto y coma por defecto
            with open(ruta_csv, 'r', encoding='utf-8-sig') as archivo:
                lector_csv = csv.DictReader(archivo, delimiter=';')
                
                for fila in lector_csv:
                    operador_archivo = fila.get('operador_red', '').strip()
                    valor_str = fila.get('valor', '').strip()
                    
                    if not operador_archivo or not valor_str:
                        continue

                    if operador_archivo not in MAPEO_CORTO_A_LARGO:
                        self.stdout.write(self.style.WARNING(f"⚠️ Operador '{operador_archivo}' no está en el diccionario. Omitiendo..."))
                        continue
                        
                    operador_oficial = MAPEO_CORTO_A_LARGO[operador_archivo]
                    
                    try:
                        valor_decimal = Decimal(valor_str.replace(',', '.'))
                        
                        obj, creado = ComponenteR.objects.update_or_create(
                            periodo=periodo,
                            operador_red=operador_oficial, 
                            defaults={'valor': valor_decimal}
                        )
                        
                        if creado:
                            registros_creados += 1
                        else:
                            registros_actualizados += 1
                            
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"❌ Error guardando {operador_archivo}: {e}"))
                                
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"❌ Error: No se encontró el archivo en {ruta_csv}"))
            return

        self.stdout.write(self.style.SUCCESS("-" * 40))
        self.stdout.write(self.style.SUCCESS("RESUMEN DE CARGA COMPONENTE R:"))
        self.stdout.write(self.style.SUCCESS(f"🔹 Nuevos: {registros_creados} | Actualizados: {registros_actualizados}"))
        self.stdout.write(self.style.SUCCESS("-" * 40))