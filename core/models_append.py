
# --- Modelos para el Dashboard de Control (Planilla Excel) ---

class IncisoControl(models.Model):
    """
    Representa las filas de la tabla izquierda del Excel (2+3, PROM, etc.)
    """
    nombre = models.CharField(max_length=100, help_text="Ej: 2+3, PROM, RYC PAIS")
    respaldo = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    asignacion = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    dev_com = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="Devengado + Compromiso")
    
    # Campos calculados se harán en la vista/property para no duplicar datos
    
    def saldo(self):
        return self.asignacion - self.dev_com
        
    def falta_asignar(self):
        return self.respaldo - self.asignacion

    def __str__(self):
        return self.nombre

class GastoOperativo(models.Model):
    """
    Representa las filas de la tabla derecha del Excel (Gastos Operativos / EMAV)
    """
    concepto = models.CharField(max_length=200, help_text="Ej: Insumos de Limpieza, Internet")
    importe_estimado = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    importe_real = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    def saldo(self):
        return self.importe_estimado - self.importe_real

    def __str__(self):
        return self.concepto
