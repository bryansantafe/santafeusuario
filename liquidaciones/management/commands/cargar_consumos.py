import csv
from datetime import datetime
from decimal import Decimal
from django.core.management.base import BaseCommand

# IMPORTANTE: Cambia 'tu_app' por el nombre real de tu aplicación
from liquidaciones.models import ConsumoHorario, Frontera 

class Command(BaseCommand):
    help = 'Carga consumos horarios desde un archivo CSV con formato matricial (días en filas, horas en columnas)'

    def add_arguments(self, parser):
        parser.add_argument('ruta_csv', type=str, help='Ruta absoluta al archivo CSV')
        # Pedimos el ID de la frontera, ya que el CSV no lo tiene explícitamente
        parser.add_argument('frontera_id', type=int, help='ID de la Frontera a la que pertenecen estos consumos')

    def handle(self, *args, **kwargs):
        ruta_csv = kwargs['ruta_csv']
        frontera_id = kwargs['frontera_id']

        # 1. Validar que la Frontera existe
        try:
            frontera = Frontera.objects.get(id=frontera_id)
            self.stdout.write(self.style.SUCCESS(f"✅ Frontera encontrada: {frontera}"))
        except Frontera.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"❌ Error: La frontera con ID {frontera_id} no existe en la base de datos."))
            return

        registros_creados = 0
        registros_actualizados = 0

        # 2. Leer el archivo
        try:
            with open(ruta_csv, 'r', encoding='utf-8') as archivo:
                lineas = archivo.readlines()
                
                # Buscar dinámicamente dónde empiezan los encabezados
                indice_header = -1
                for i, linea in enumerate(lineas):
                    if linea.startswith('Fecha'):
                        indice_header = i
                        break
                
                if indice_header == -1:
                    self.stdout.write(self.style.ERROR("❌ No se encontró la fila de encabezados (debe empezar con la palabra 'Fecha')."))
                    return

                # Usamos DictReader a partir de la fila donde encontramos 'Fecha'
                lector_csv = csv.DictReader(lineas[indice_header:], delimiter=';')

                # 3. Iterar sobre cada día (fila del CSV)
                for fila in lector_csv:
                    fecha_str = fila.get('Fecha', '').strip()
                    if not fecha_str or fecha_str.lower() == 'total':
                        continue # Saltar filas vacías o subtotales
                        
                    # Parsear la fecha de DD-MM-YYYY a objeto Date de Python
                    try:
                        # Reemplazamos / por - en caso de que alguna fecha venga con slash
                        fecha_str = fecha_str.replace('/', '-')
                        fecha_obj = datetime.strptime(fecha_str, '%d-%m-%Y').date()
                    except ValueError:
                        self.stdout.write(self.style.WARNING(f"⚠️ Formato de fecha inválido en la fila: {fecha_str}. Omitiendo..."))
                        continue

                    # 4. Iterar sobre las 24 columnas de horas ('0:00' a '23:00')
                    for hora_csv in range(24):
                        columna_hora = f"{hora_csv}:00"
                        valor_str = fila.get(columna_hora, '0').strip()
                        
                        try:
                            consumo_activo = Decimal(valor_str)
                        except:
                            consumo_activo = Decimal('0')

                        # 5. Guardar en BD (update_or_create evita duplicados si corres el script 2 veces)
                        obj, creado = ConsumoHorario.objects.update_or_create(
                            frontera=frontera,
                            fecha=fecha_obj,
                            hora=hora_csv + 1,  # Guardamos la hora en formato 1 a 24
                            defaults={
                                'consumo_activo': consumo_activo,
                                'consumo_reactivo': Decimal('0'), # El CSV no proporciona este dato
                                'es_estimado': False
                            }
                        )
                        
                        if creado:
                            registros_creados += 1
                        else:
                            registros_actualizados += 1

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"❌ Error: No se encontró el archivo en la ruta {ruta_csv}"))
            return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error procesando el archivo: {e}"))
            return

        # 6. Imprimir resumen final
        self.stdout.write(self.style.SUCCESS("-" * 40))
        self.stdout.write(self.style.SUCCESS("RESUMEN DE CARGA DE CONSUMOS HORARIOS:"))
        self.stdout.write(self.style.SUCCESS(f"🔹 Registros creados: {registros_creados}"))
        self.stdout.write(self.style.SUCCESS(f"🔹 Registros actualizados: {registros_actualizados}"))
        self.stdout.write(self.style.SUCCESS("-" * 40))