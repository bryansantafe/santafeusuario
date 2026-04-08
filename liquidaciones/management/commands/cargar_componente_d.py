import csv
from decimal import Decimal
from datetime import datetime
from django.core.management.base import BaseCommand

# Reemplaza 'tu_app' por el nombre real de tu aplicación
from liquidaciones.models import ComponenteD, Periodo 

class Command(BaseCommand):
    help = 'Carga los datos desde un archivo CSV con estructura vertical (Operador, Nivel, Cargo)'

    def add_arguments(self, parser):
        parser.add_argument('ruta_csv', type=str, help='Ruta absoluta al archivo CSV')
        parser.add_argument('fecha_periodo', type=str, help='Fecha del periodo en formato MM/YYYY (ej: 01/2026)')

    def handle(self, *args, **kwargs):
        ruta_csv = kwargs['ruta_csv']
        fecha_periodo_str = kwargs['fecha_periodo']

        # --- DICCIONARIO TRADUCTOR ACTUALIZADO ---
        # Basado en los nombres exactos que vienen en tu nuevo archivo "add.xlsx - Sheet1.csv"
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

        # 1. Buscar el Periodo
        try:
            fecha_obj = datetime.strptime(fecha_periodo_str, '%m/%Y').replace(day=1).date()
            periodo = Periodo.objects.get(fecha_mes=fecha_obj)
            self.stdout.write(self.style.SUCCESS(f"✅ Periodo encontrado: {periodo}"))
        except Periodo.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"❌ Error: El periodo con fecha {fecha_periodo_str} no existe en la BD."))
            return

        registros_creados = 0
        registros_actualizados = 0

        # 2. Abrir y leer el archivo CSV
        try:
            with open(ruta_csv, 'r', encoding='utf-8') as archivo:
                lector_csv = csv.DictReader(archivo)
                
                for fila in lector_csv:
                    # Capturamos las nuevas columnas
                    operador_archivo = fila.get('operador_red', '').strip()
                    nivel_str = fila.get('nivel_tension', '').strip()
                    valor_str = fila.get('Cargo Único Transitorio ($/kWh)', '').strip()
                    
                    # Ignorar filas vacías
                    if not operador_archivo or not valor_str:
                        continue

                    # Verificamos si existe en el diccionario
                    if operador_archivo not in MAPEO_CORTO_A_LARGO:
                        self.stdout.write(self.style.WARNING(f"⚠️ Operador '{operador_archivo}' no está en el diccionario. Omitiendo..."))
                        continue
                        
                    operador_oficial = MAPEO_CORTO_A_LARGO[operador_archivo]
                    
                    try:
                        # Convertimos a entero el nivel y a decimal el valor
                        nivel = int(float(nivel_str)) 
                        valor_decimal = Decimal(valor_str.replace(',', '.'))
                        
                        # 3. Guardar en la base de datos
                        obj, creado = ComponenteD.objects.update_or_create(
                            periodo=periodo,
                            operador_red=operador_oficial, 
                            nivel_tension=nivel,
                            defaults={'valor': valor_decimal}
                        )
                        
                        if creado:
                            registros_creados += 1
                        else:
                            registros_actualizados += 1
                            
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"❌ Error guardando {operador_archivo} - Nivel {nivel_str}: {e}"))
                                
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"❌ Error: No se encontró el archivo en la ruta {ruta_csv}"))
            return

        # 4. Imprimir el resumen
        self.stdout.write(self.style.SUCCESS("-" * 40))
        self.stdout.write(self.style.SUCCESS("RESUMEN DE CARGA:"))
        self.stdout.write(self.style.SUCCESS(f"🔹 Registros nuevos creados: {registros_creados}"))
        self.stdout.write(self.style.SUCCESS(f"🔹 Registros actualizados: {registros_actualizados}"))
        self.stdout.write(self.style.SUCCESS("-" * 40))