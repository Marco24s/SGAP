from django.core.management.base import BaseCommand
from core.models import UnidadComponente

class Command(BaseCommand):
    help = 'Limpia Unidades Componentes antiguas de prueba (sin sigla)'

    def handle(self, *args, **options):
        # Delete units where sigla is null (the old test data)
        deleted_count, _ = UnidadComponente.objects.filter(sigla__isnull=True).delete()
        self.stdout.write(self.style.SUCCESS(f'Se eliminaron {deleted_count} unidades de prueba antiguas.'))
