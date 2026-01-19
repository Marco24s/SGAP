from django.test import TestCase, Client
from django.urls import reverse
from core.models import EstructuraProgramatica, UnidadComponente, ClasificadorGasto, FuenteFinanciamiento
from finance.models import Credito, Asignacion

class DistributionViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Setup Data
        self.program = EstructuraProgramatica.objects.create(nivel=1, codigo="01", descripcion="Prog")
        self.ff = FuenteFinanciamiento.objects.create(codigo="11", descripcion="Tesoro")
        self.credito = Credito.objects.create(programa=self.program, fuente=self.ff, monto_total=1000, anio=2026, trimestre=1)
        self.uucc = UnidadComponente.objects.create(nombre="U1", codigo="U1", es_ejecutora=True)
        self.cg = ClasificadorGasto.objects.create(nivel=1, codigo="3", descripcion="Servicios") # Inciso 3 is simple
        
    def test_dashboard_load(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Administrador de Programa")

    def test_list_credits_load(self):
        response = self.client.get(reverse('finance:lista_creditos'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Créditos Disponibles")

    def test_distribute_view_load(self):
        url = reverse('finance:distribuir_credito', args=[self.credito.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Contexto del Crédito")
