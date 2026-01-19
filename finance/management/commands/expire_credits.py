from django.core.management.base import BaseCommand
from django.utils import timezone
from finance.models import Credito

class Command(BaseCommand):
    help = 'Caduca los créditos del año anterior (Regla 5.1)'

    def handle(self, *args, **options):
        now = timezone.now()
        current_year = now.year
        
        # Logic: Find all CREDITS that are 'VIGENTE' and from a previous year
        # Actually, rule says "El 31 de diciembre... todo crédito sobrante... pasa a Caducado"
        # So running this on Jan 1st should expire everything from year < current_year
        
        credits_to_expire = Credito.objects.filter(estado='VIGENTE', anio__lt=current_year)
        count = credits_to_expire.count()
        
        credits_to_expire.update(estado='CADUCADO')
        
        self.stdout.write(self.style.SUCCESS(f'Se han caducado {count} créditos del año anterior.'))
