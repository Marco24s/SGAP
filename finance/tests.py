from django.test import TestCase
from django.core.exceptions import ValidationError
from core.models import EstructuraProgramatica, UnidadComponente, ClasificadorGasto, FuenteFinanciamiento
from finance.models import Credito, Asignacion

class FinanceRulesTest(TestCase):
    def setUp(self):
        # Setup basic data
        self.program = EstructuraProgramatica.objects.create(nivel=1, codigo="01", descripcion="Programa 1")
        self.subprog = EstructuraProgramatica.objects.create(nivel=2, codigo="01", descripcion="Subprograma 1", padre=self.program)
        self.uucc = UnidadComponente.objects.create(nombre="Unidad Test", codigo="U001", es_ejecutora=True)
        self.ff = FuenteFinanciamiento.objects.create(codigo="11", descripcion="Tesoro", es_fiscal=True)
        
        # Classifiers
        self.cg_inciso_1 = ClasificadorGasto.objects.create(nivel=1, codigo="1", descripcion="Personal")
        self.cg_inciso_4 = ClasificadorGasto.objects.create(nivel=1, codigo="4", descripcion="Bienes de Uso")
        self.cg_parcial_1 = ClasificadorGasto.objects.create(nivel=3, codigo="1", descripcion="Retribuciones", padre=self.cg_inciso_1) # Incorrect parent skip for brevity? 
        # Correct hierarchy: Inciso -> Principal -> Parcial. 
        # Actually let's do it right.
        self.cg_principal_1 = ClasificadorGasto.objects.create(nivel=2, codigo="1", descripcion="Principal", padre=self.cg_inciso_1)
        self.cg_parcial_1.padre = self.cg_principal_1
        self.cg_parcial_1.save()
        
        self.credito = Credito.objects.create(programa=self.program, fuente=self.ff, monto_total=1000, anio=2026, trimestre=1)
        
    def test_integrity_sum_check(self):
        # Assign 600
        Asignacion.objects.create(
            uucc=self.uucc, credito_origen=self.credito, 
            clasificador_gasto=self.cg_parcial_1, monto=600, trimestre=1
        )
        
        # Try assigning 500 more (Total 1100 > 1000)
        with self.assertRaises(ValidationError):
            a2 = Asignacion(
                uucc=self.uucc, credito_origen=self.credito,
                clasificador_gasto=self.cg_parcial_1, monto=500, trimestre=1
            )
            a2.full_clean()

    def test_granularity_inciso_1(self):
        # Attempt to assign directly to Inciso 1 (Level 1) -> Should fail
        with self.assertRaisesMessage(ValidationError, "debe detallar hasta Partida Parcial"):
            a = Asignacion(
                uucc=self.uucc, credito_origen=self.credito,
                clasificador_gasto=self.cg_inciso_1, monto=100, trimestre=1
            )
            a.full_clean()

    def test_obra_restriction_inciso_4(self):
        # Attempt to assign Inciso 4 without Obra
        with self.assertRaisesMessage(ValidationError, "es obligatorio asociar una Obra"):
            a = Asignacion(
                uucc=self.uucc, credito_origen=self.credito,
                clasificador_gasto=self.cg_inciso_4, monto=100, trimestre=1
            )
            a.full_clean()
            
        # With Obra
        obra_node = EstructuraProgramatica.objects.create(nivel=4, codigo="55", descripcion="Obra Test", padre=self.subprog)
        a = Asignacion(
            uucc=self.uucc, credito_origen=self.credito,
            clasificador_gasto=self.cg_inciso_4, monto=100, trimestre=1,
            obra=obra_node
        )
        try:
            a.full_clean()
        except ValidationError:
            self.fail("Should not raise ValidationError with correct Work info")
