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
