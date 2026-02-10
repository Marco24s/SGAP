from django.db import models
from django.utils import timezone

class TipoPrenda(models.Model):
    CATEGORIA_CHOICES = [
        ('vuelo', 'Ropa de Vuelo'),
        ('trabajo', 'Ropa de Trabajo'),
    ]

    nombre = models.CharField(max_length=100) # Ej: "Casco de Vuelo", "Campera"
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    vida_util_sugerida = models.PositiveIntegerField(help_text="En meses", default=12)

    def __str__(self):
        return f"{self.nombre} ({self.get_categoria_display()})"

class Dotacion(models.Model):
    """Define qué debe tener cada rol"""
    ROLES_CHOICES = [
        ('piloto', 'Piloto'),
        ('tripulante', 'Tripulante'),
        ('mecanico', 'Mecánico'),
        ('administrativo', 'Administrativo'),
        ('otro', 'Otro'),
    ]

    rol = models.CharField(max_length=20, choices=ROLES_CHOICES)
    tipo_prenda = models.ForeignKey(TipoPrenda, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    renovacion_int = models.PositiveIntegerField(help_text="Intervalo de renovación en meses", default=12)

    def __str__(self):
        return f"{self.rol} - {self.tipo_prenda} (x{self.cantidad})"

class Personal(models.Model):
    GRADOS_CHOICES = [
        ('CF', 'Capitán de Fragata'),
        ('CC', 'Capitán de Corbeta'),
        ('TN', 'Teniente de Navío'),
        ('TF', 'Teniente de Fragata'),
        ('TC', 'Teniente de Corbeta'),
        ('GU', 'Guardiamarina'),
        ('SM', 'Suboficial Mayor'),
        ('SP', 'Suboficial Principal'),
        ('SI', 'Suboficial Primero'),
        ('SS', 'Suboficial Segundo'),
        ('CP', 'Cabo Principal'),
        ('CI', 'Cabo Primero'),
        ('CS', 'Cabo Segundo'),
        ('MR', 'Marinero Primero'),
        ('M2', 'Marinero Segundo'),
        ('CV', 'Civil'),
    ]

    ROLES_CHOICES = [
        ('piloto', 'Piloto'),
        ('tripulante', 'Tripulante'),
        ('mecanico', 'Mecánico'),
        ('administrativo', 'Administrativo'),
        ('otro', 'Otro'),
    ]

    legajo = models.CharField(max_length=20, unique=True)
    apellido = models.CharField(max_length=100)
    nombre = models.CharField(max_length=100)
    grado = models.CharField(max_length=2, choices=GRADOS_CHOICES)
    unidad = models.CharField(max_length=100, default='Escuadrilla Aeronaval')
    rol = models.CharField(max_length=20, choices=ROLES_CHOICES)
    estado = models.BooleanField(default=True, help_text="Activo / Baja")

    def __str__(self):
        return f"{self.grado} {self.apellido} {self.nombre}"

    class Meta:
        verbose_name_plural = "Personal"

class Prenda(models.Model):
    ESTADO_CHOICES = [
        ('deposito', 'En Depósito'),
        ('asignada', 'Asignada'),
        ('reparacion', 'En Reparación'),
        ('fs', 'Fuera de Servicio'),
        ('baja', 'Baja Definitiva'),
    ]

    # Dejamos tipo para compatibilidad o lo migramos luego, pero ahora usamos TipoPrenda
    tipo_prenda = models.ForeignKey(TipoPrenda, on_delete=models.SET_NULL, null=True, blank=True)
    
    descripcion = models.CharField(max_length=200, help_text="Ej: Marca, Modelo específico, etc.")
    talle = models.CharField(max_length=20)
    codigo_interno = models.CharField(max_length=50, unique=True)
    fecha_alta = models.DateField(default=timezone.now)
    vida_util_meses = models.PositiveIntegerField(help_text="Vida útil estimada en meses", blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='deposito')

    def __str__(self):
        tipo_nombre = self.tipo_prenda.nombre if self.tipo_prenda else "Sin Tipo"
        return f"{tipo_nombre} - {self.descripcion} - {self.talle}"
    
    def save(self, *args, **kwargs):
        if not self.vida_util_meses and self.tipo_prenda:
            self.vida_util_meses = self.tipo_prenda.vida_util_sugerida
        super().save(*args, **kwargs)

class Asignacion(models.Model):
    MOTIVO_CHOICES = [
        ('inicial', 'Dotación Inicial'),
        ('reemplazo', 'Reemplazo'),
        ('desgaste', 'Desgaste'),
        ('campana', 'Campaña'),
        ('otro', 'Otro'),
    ]

    personal = models.ForeignKey(Personal, on_delete=models.CASCADE, related_name='asignaciones')
    prenda = models.ForeignKey(Prenda, on_delete=models.CASCADE, related_name='historial_asignaciones')
    fecha_entrega = models.DateField(default=timezone.now)
    fecha_devolucion = models.DateField(null=True, blank=True)
    motivo = models.CharField(max_length=20, choices=MOTIVO_CHOICES)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.prenda} -> {self.personal}"

class Movimiento(models.Model):
    TIPO_MOVIMIENTO_CHOICES = [
        ('alta', 'Alta'),
        ('asignacion', 'Asignación'),
        ('devolucion', 'Devolución'),
        ('reparacion', 'Envío a Reparación'),
        ('baja', 'Baja'),
        ('modificacion', 'Modificación de Datos'),
    ]

    prenda = models.ForeignKey(Prenda, on_delete=models.CASCADE, related_name='movimientos')
    tipo = models.CharField(max_length=20, choices=TIPO_MOVIMIENTO_CHOICES)
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.CharField(max_length=100, help_text="Usuario que realizó la acción")
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"{self.tipo} - {self.prenda} ({self.fecha})"
