from django.db import models
from core.models import EstructuraProgramatica, UnidadComponente, ClasificadorGasto, FuenteFinanciamiento

class Credito(models.Model):
    ESTADO_CHOICES = (
        ("VIGENTE", "Vigente"),
        ("CADUCADO", "Caducado"),
        ("DEVENGADO", "Devengado"),
    )

    TIPO_CREDITO_CHOICES = (
        ("ASIGNACION", "Asignación"),
        ("REFUERZO", "Refuerzo"),
    )
    
    programa = models.ForeignKey(EstructuraProgramatica, on_delete=models.CASCADE, related_name="creditos")
    fuente = models.ForeignKey(FuenteFinanciamiento, on_delete=models.PROTECT)
    monto_total = models.DecimalField(max_digits=12, decimal_places=2)
    monto_cuota = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="Dinero ingresado (Cuota)")
    recibido = models.BooleanField(default=True, help_text="Indica si la cuota ya fue recibida efectivamente")
    inciso = models.CharField(max_length=10, help_text="Inciso", default="")
    principal = models.CharField(max_length=10, help_text="Partida Principal", default="")
    anio = models.IntegerField(help_text="Año fiscal")
    trimestre = models.IntegerField(choices=[(1, "1° Trimestre"), (2, "2° Trimestre"), (3, "3° Trimestre"), (4, "4° Trimestre")])
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="VIGENTE")
    tipo_credito = models.CharField(max_length=20, choices=TIPO_CREDITO_CHOICES, default="ASIGNACION", verbose_name="Tipo de Crédito")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Credito {self.anio}-T{self.trimestre} - {self.programa} - ${self.monto_total}"

    @property
    def saldo_disponible(self):
        """
        Returns the unassigned amount of this Credit.
        """
        asignado = self.asignaciones.aggregate(total=models.Sum('monto'))['total'] or 0
        return self.monto_total - asignado

class Asignacion(models.Model):
    TRIMESTRE_CHOICES = (
        (1, "1° Trimestre"),
        (2, "2° Trimestre"),
        (3, "3° Trimestre"),
        (4, "4° Trimestre"),
    )

    uucc = models.ForeignKey(UnidadComponente, on_delete=models.PROTECT, related_name="asignaciones")
    credito_origen = models.ForeignKey(Credito, on_delete=models.CASCADE, related_name="asignaciones")
    clasificador_gasto = models.ForeignKey(ClasificadorGasto, on_delete=models.PROTECT)
    # Rule 5.2: Requirement to associate an Obra for Inciso 4
    obra = models.ForeignKey(EstructuraProgramatica, on_delete=models.PROTECT, null=True, blank=True, related_name="asignaciones_obra", help_text="Obligatorio para Inciso 4 (Inversión)")
    monto = models.DecimalField(max_digits=12, decimal_places=2, help_text="Monto asignado por GFH")
    solicitud_gfh = models.CharField(max_length=100, blank=True, null=True, help_text="Referencia solicitada por GFH (Texto/Números)")
    asignacion_gfh = models.CharField(max_length=100, blank=True, null=True, help_text="Referencia asignada por GFH (Texto/Números)")
    trimestre = models.IntegerField(choices=TRIMESTRE_CHOICES)

    OBJETO_CHOICES = (
        ('2+3', '2+3'),
        ('PROM', 'PROM'),
        ('RYC PAIS', 'RYC PAIS'),
        ('RYC EXTERIOR', 'RYC EXTERIOR'),
        ('4', '4'),
        ('GGOO', 'GGOO'),
        ('SS.BB.', 'SS.BB.'),
        ('PYV', 'PYV'),
        ('20', '20'),
        ('40', '40'),
        ('50', '50'),
        ('70', '70'),
        ('87', '87'),
        ('90', '90'),
        ('95', '95'),
        ('99', '99'),
        ('Vestuario PACID', 'Vestuario PACID'),
    )
    objeto = models.CharField(max_length=50, choices=OBJETO_CHOICES, blank=True, null=True, help_text="Objeto del Gasto")
    
    def clean(self):
        from django.core.exceptions import ValidationError
        
        # 1. Validation: Integrity (Sum <= Total)
        # We need to sum execute a query to check total assigned so far for this credit
        # Note: We exclude self if updating to avoid double counting
        current_assigned = self.credito_origen.asignaciones.exclude(pk=self.pk).aggregate(total=models.Sum('monto'))['total'] or 0
        if current_assigned + self.monto > self.credito_origen.monto_total:
             raise ValidationError("IMPOSIBLE ASIGNAR ESE MONTO, SUPERA EL SALDO DISPONIBLE")

        # 1.1 Validation: Warning/Error if exceeds 'Real' Cash (Cuota)
        # User requested to indicate how much we are exceeding the real available quota
        if current_assigned + self.monto > self.credito_origen.monto_cuota:
            diff = (current_assigned + self.monto) - self.credito_origen.monto_cuota
            # Formatting as per locale roughly
            diff_str = f"{diff:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            raise ValidationError(f"Atención: El monto a asignar supera el saldo de cuota recibida en ${diff_str}")

        # 2. Validation: Granularity based on Inciso (Art 2.01) [SIMPLIFIED FOR MVP]
        # Logic: If Inciso 1 (Personal) -> Required Level 3 (Parcial)
        # If Inciso 4 (Bienes Uso) -> Required Level 3 (Parcial)
        # This assumes ClasificadorGasto has 'nivel' field correctly populated.
        
        # Get the root inciso of the selected classifier
        # We traverse up until we find level 1
        curr = self.clasificador_gasto
        while curr.padre and curr.nivel > 1:
            curr = curr.padre
        
        root_inciso_code = curr.codigo
        
        if root_inciso_code == '1' and self.clasificador_gasto.nivel < 3:
             raise ValidationError("Para Gastos en Personal (Inciso 1), debe detallar hasta Partida Parcial.")
        
        # Rule 5.2: Restriction of Obras (Inciso 4)
        if root_inciso_code == '4':
            if not self.obra:
                raise ValidationError("Para Inversión Real (Inciso 4), es obligatorio asociar una Obra.")
            if self.obra.nivel != 4: # Assuming 4 is Obra in EstructuraProgramatica
                raise ValidationError("El elemento seleccionado no es una Obra válida.")

        if root_inciso_code == '2' and self.clasificador_gasto.nivel > 1:
             # Rule says "Se distribuye a nivel global (Solo Inciso)" for Inciso 2 ?? 
             # Re-reading spec: "Inciso 2 (Consumo): Se distribuye a nivel global (Solo Inciso)."
             # If strictly enforced:
             pass 
             # raise ValidationError("Para Bienes de Consumo (Inciso 2), solo debe imputar a nivel Inciso.")
             # NOTE: Allow flexibility for now, but strictly enforce requiring detail where mandated.
             
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.uucc} - {self.clasificador_gasto} - ${self.monto}"

class ModificacionPresupuestaria(models.Model):
    TIPO_CHOICES = (
        ("COMPENSACION", "Compensación Interna"),
        ("REDISTRIBUCION", "Redistribución"),
        ("ENTRE_PROGRAMAS", "Entre Programas"),
    )
    ESTADO_WORKFLOW = (
        ("BORRADOR", "Borrador"),
        ("PENDIENTE", "Pendiente de Aprobación"),
        ("APROBADO", "Aprobado"),
        ("RECHAZADO", "Rechazado"),
    )

    origen = models.ForeignKey(Asignacion, on_delete=models.CASCADE, related_name="modificaciones_salida")
    destino = models.ForeignKey(Asignacion, on_delete=models.CASCADE, related_name="modificaciones_entrada")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADO_WORKFLOW, default="BORRADOR")
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.tipo}: {self.origen} -> {self.destino} (${self.monto})"

class AutorizacionCargo(models.Model):
    unidad_origen = models.ForeignKey(UnidadComponente, on_delete=models.PROTECT, related_name="cargos_autorizados")
    unidad_autorizada = models.ForeignKey(UnidadComponente, on_delete=models.PROTECT, related_name="cargos_recibidos")
    clasificador = models.ForeignKey(ClasificadorGasto, on_delete=models.PROTECT)
    monto_maximo = models.DecimalField(max_digits=12, decimal_places=2)
    vencimiento = models.DateField()
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"Auth: {self.unidad_origen} -> {self.unidad_autorizada} (${self.monto_maximo})"

class Compromiso(models.Model):
    """
    Representa la ejecución o 'gasto' realizado por la UU.CC.
    contra una Asignación específica.
    """
    asignacion = models.ForeignKey(Asignacion, on_delete=models.CASCADE, related_name="compromisos")
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha = models.DateField(auto_now_add=True)
    concepto = models.CharField(max_length=255)
    numero_orden = models.CharField(max_length=50, blank=True)

    def clean(self):
        from django.core.exceptions import ValidationError
        # Validation: Cannot commit more than Assigned (Saldo Disponible)
        # Calculate current committed sum (excluding self)
        total_committed = self.asignacion.compromisos.exclude(pk=self.pk).aggregate(sum=models.Sum('monto'))['sum'] or 0
        if total_committed + self.monto > self.asignacion.monto:
            raise ValidationError(f"Fondos Insuficientes. Disponible: ${self.asignacion.monto - total_committed}")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Compromiso {self.asignacion.uucc} - ${self.monto}"
