from django.core.management.base import BaseCommand
from core.models import EstructuraProgramatica, UnidadComponente, ClasificadorGasto, FuenteFinanciamiento
from finance.models import Credito
from django.utils import timezone

class Command(BaseCommand):
    help = 'Carga datos iniciales de prueba para el sistema SGAP con UU.CC. reales'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando carga de datos reales...')

        # 1. Borrar datos anteriores (Opcional, pero util para limpiar)
        # Uncomment if you want to wipe before load
        # UnidadComponente.objects.all().delete()
        
        # 4. Unidades Componentes (Lista Real)
        uucc_list = [
            # COAN
            ('686000', 'SISE', 'SERVICIO DE SEGURIDAD AERONAVAL'),
            ('603000', 'MUAN', 'MUSEO DE LA AVIACIÓN NAVAL'),
            ('252000', 'COAN', 'COMANDO DE LA AVIACIÓN NAVAL'),
            
            # BAPI
            ('102000', 'BAPI', 'BASE AERONAVAL PUNTA INDIO'),
            ('410000', 'EA1E', 'ESCUADRILLA AERONAVAL DE LA ESCUELA DE AVIACIÓN NAVAL'),
            ('407000', 'EA1V', 'ESCUADRILLA AERONAVAL DE VIGILANCIA MARÍTIMA'),
            ('388000', 'EAN1', 'ESCUADRA AERONAVAL N° 1'),
            ('430000', 'ESAN', 'ESCUELA DE AVIACIÓN NAVAL'),
            ('255000', 'ETPI', 'ESTACIÓN SECUNDARIA DE COMUNICACIONES NAVALES PUNTA INDIO'),
            ('716000', 'TVPI', 'TALLER AERONAVAL PUNTA INDIO'),

            # FAE2
            ('096000', 'BACE', 'BASE AERONAVAL "COMANDANTE ESPORA"'),
            ('220000', 'CIFA', 'CENTRO DE ADIESTRAMIENTO DE LA FUERZA AERONAVAL N° 2'),
            ('398000', 'EA2S', 'ESCUADRILLA AERONAVAL ANTISUBMARINA'),
            ('402000', 'EA32', 'SEGUNDA ESCUADRILLA AERONAVAL DE CAZA Y ATAQUE'),
            ('414000', 'EAH1', 'PRIMERA ESCUADRILLA AERONAVAL DE HELICÓPTEROS'),
            ('415000', 'EAH2', 'SEGUNDA ESCUADRILLA AERONAVAL DE HELICÓPTEROS'),
            ('500000', 'FAE2', 'FUERZA AERONAVAL N° 2'),
            ('392000', 'EAN3', 'ESCUADRA AERONAVAL N° 3'),
            ('096000', 'ETCE', 'ESTACIÓN SECUNDARIA DE COMUNICACIONES NAVALES "COMANDANTE ESPORA"'),

            # FAE3
            ('108000', 'BAAZ', 'BASE AERONAVAL "ALMIRANTE ZAR"'),
            ('106000', 'BARD', 'BASE AERONAVAL RIO GRANDE "PIONEROS AERONAVALES EN EL POLO SUR"'),
            ('406000', 'EA6E', 'ESCUADRILLA AERONAVAL DE EXPLORACIÓN'),
            ('397000', 'EAN6', 'ESCUADRA AERONAVAL N° 6'),
            ('108000', 'ETZR', 'ESTACIÓN PRINCIPAL DE COMUNICACIONES NAVALES "ALMIRANTE ZAR"'),
            ('502000', 'FAE3', 'FUERZA AERONAVAL N° 3'),
            ('719000', 'TVAZ', 'TALLER AERONAVAL ALMIRANTE ZAR'),
        ]

        for codigo, sigla, nombre in uucc_list:
            UnidadComponente.objects.update_or_create(
                sigla=sigla,
                defaults={
                    'codigo': codigo,
                    'nombre': nombre,
                    'es_ejecutora': True # Assuming all loaded units execute budget?
                }
            )

        self.stdout.write(self.style.SUCCESS(f'Se actualizaron {len(uucc_list)} Unidades Componentes.'))
