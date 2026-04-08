import pandas as pd
import numpy as np
from django.core.management.base import BaseCommand
from data.models import Agente, Recurso
from datetime import datetime

class Command(BaseCommand):
    help = 'Importa agentes y recursos desde archivos CSV'

    def handle(self, *args, **options):
        # 1. CARGAR AGENTES
        '''
        self.stdout.write(self.style.SUCCESS('Iniciando carga de Agentes...'))
        
        df_agentes = pd.read_excel('Listado_Agentes-3.xlsx')
        
        # Limpieza de fechas: reemplazamos valores vacíos por None
        df_agentes = df_agentes.replace({np.nan: None})

        for _, row in df_agentes.iterrows():
            agente, created = Agente.objects.update_or_create(
                agente_id=row['Código SIC'],
                defaults={
                    'nombre_agente': row['Nombre Agente'],
                    'actividad': row['Actividad'],
                    'clasificacion': row['Clasificación'],
                    'estado': row['Estado'],
                    'fecha_registro': row['Fecha Registro'],
                    'fecha_fin': row['Fecha Fin'] if row['Fecha Fin'] else None
                }
            )
            if created:
                self.stdout.write(f"Agente creado: {agente.nombre_agente}")
        '''
        # 2. CARGAR RECURSOS
        self.stdout.write(self.style.SUCCESS('Iniciando carga de Recursos...'))
        # Nota: Usamos read_csv si el archivo es .csv, o read_excel si es .xlsx
        df_recursos = pd.read_excel('Listado_Recursos_Generacion-2.xlsx')
        df_recursos = df_recursos.replace({np.nan: None})

        for _, row in df_recursos.iterrows():
            nombre_busqueda = row['Agente Representante'].strip()
            agente = Agente.objects.filter(nombre_agente__icontains=nombre_busqueda).first()

            if agente:
                self.stdout.write(f"Insertando .........: {agente}")
                Recurso.objects.update_or_create(
                    recurso_id=row['Código SIC'],
                    defaults={
                        'agente': agente,
                        'nombre_recurso': row['Nombre Recurso'],
                        'capacidad_efectiva_neta': row['Capacidad Efectiva Neta [MW]'],
                        'tipo_tecnologia': row['Tipo Generación'],
                        # --- NUEVOS MAPEOS ---
                        'fecha_operacion': row['Fecha Operación'],
                        'municipio': row['Municipio'],
                        'departamento': row['Departamento'],
                        'combustible': row['Combustible por Defecto'],
                        'estado_recurso': row['Estado Recurso'],
                        'clasificacion': row['Clasificación']
                    }
                )
                self.stdout.write(f"Recurso creado: {Recurso.nombre_recurso}")
            else:
                self.stdout.write(self.style.WARNING(f"Agente no encontrado para: {nombre_busqueda}"))