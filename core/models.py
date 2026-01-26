from django.db import models

class EstructuraProgramatica(models.Model):
    NIVEL_CHOICES = (
        (1, "Programa"),
        (2, "Subprograma"),
        (3, "Proyecto"),
        (4, "Obra"),
        (5, "Actividad"),
    )
    nivel = models.IntegerField(choices=NIVEL_CHOICES)
    codigo = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=255)
    padre = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE, related_name="hijos")

    def __str__(self):
        return f"{self.get_nivel_display()} {self.codigo} - {self.descripcion}"

class UnidadComponente(models.Model):
    nombre = models.CharField(max_length=255)
    codigo = models.CharField(max_length=50) # Removed unique=True to allow shared budget codes
    sigla = models.CharField(max_length=20, unique=True, null=True) # Added Sigla as unique identifier
    es_ejecutora = models.BooleanField(default=False, help_text="Solo UU.CC. del Plan Bienal pueden ejecutar gasto")

    def __str__(self):
        return f"{self.codigo} ({self.sigla}) - {self.nombre}"

class ClasificadorGasto(models.Model):
    NIVEL_CHOICES = (
        (1, "Inciso"),
        (2, "Partida Principal"),
        (3, "Partida Parcial"),
        (4, "Partida Subparcial"),
    )
    codigo = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=255)
    nivel = models.IntegerField(choices=NIVEL_CHOICES)
    padre = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE, related_name="hijos")

    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"

class FuenteFinanciamiento(models.Model):
    CODIGO_CHOICES = (
        ("11", "Tesoro Nacional"),
        ("13", "Recursos Específicos"),
    )
    codigo = models.CharField(max_length=10, choices=CODIGO_CHOICES)
    descripcion = models.CharField(max_length=255)
    es_fiscal = models.BooleanField(default=True, help_text="Indica si es dinero fiscal")

    def __str__(self):
        return f"FF {self.codigo} - {self.descripcion}"

# --- Modelos para el Dashboard de Control (Planilla Excel) ---

class IncisoControl(models.Model):
    """
    Representa las filas de la tabla izquierda del Excel (2+3, PROM, etc.)
    """
    nombre = models.CharField(max_length=100, help_text="Ej: 2+3, PROM, RYC PAIS")
    cuatrigrama = models.CharField(max_length=10, default="EMAV", help_text="EMAV, BAPI, FAE2, etc.")
    ff = models.CharField(max_length=10, blank=True, null=True, help_text="Fuente de Financiamiento (Ej: 11)")
    programa = models.CharField(max_length=20, blank=True, null=True, help_text="Ej: 01, 16")
    subprograma = models.CharField(max_length=20, blank=True, null=True, help_text="Ej: 02, 04")
    respaldo = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    asignacion = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    dev_com = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="Devengado + Compromiso")
    nota = models.TextField(blank=True, null=True, help_text="Observaciones o notas adicionales")
    updated_at = models.DateTimeField(auto_now=True, help_text="Fecha de última modificación")
    
    @property
    def saldo(self):
        return self.asignacion - self.dev_com
        
    @property
    def falta_asignar(self):
        return self.respaldo - self.asignacion

    def __str__(self):
        return self.nombre

class HistorialInciso(models.Model):
    inciso = models.ForeignKey(IncisoControl, related_name='historial', on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    nota = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-fecha']

class GastoOperativo(models.Model):
    """
    Representa las filas de la tabla derecha del Excel (Gastos Operativos / EMAV)
    """
    concepto = models.CharField(max_length=200, help_text="Ej: Insumos de Limpieza, Internet")
    importe_estimado = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    importe_real = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    @property
    def saldo(self):
        return self.importe_estimado - self.importe_real

    def __str__(self):
        return self.concepto
