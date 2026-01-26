from core.models import IncisoControl, GastoOperativo

# Limpiar datos anteriores
IncisoControl.objects.all().delete()
GastoOperativo.objects.all().delete()

# Crear Incisos (Tabla Izquierda)
incisos_data = [
    {"nombre": "2+3", "asignacion": 15000000, "dev_com": 5000000},
    {"nombre": "PROM", "asignacion": 2000000, "dev_com": 0},
    {"nombre": "RYC PAIS", "asignacion": 3500000, "dev_com": 1200000},
    {"nombre": "RYC EXTERIOR", "asignacion": 5000000, "dev_com": 4500000},
    {"nombre": "GGOO", "asignacion": 1000000, "dev_com": 200000},
]

for item in incisos_data:
    IncisoControl.objects.create(
        nombre=item["nombre"],
        respaldo=item["asignacion"] * 1.2, # Un poco más que la asignación
        asignacion=item["asignacion"],
        dev_com=item["dev_com"]
    )

# Crear Gastos Operativos (Tabla Derecha)
gastos_data = [
    {"concepto": "Insumos de Limpieza", "estimado": 2000000, "real": 150000},
    {"concepto": "Internet", "estimado": 1800000, "real": 1800000}, # Saldo 0
    {"concepto": "Insumos Informáticos", "estimado": 2500000, "real": 3000000}, # Saldo Negativo
    {"concepto": "Vehículos", "estimado": 2000000, "real": 500000},
]

for item in gastos_data:
    GastoOperativo.objects.create(
        concepto=item["concepto"],
        importe_estimado=item["estimado"],
        importe_real=item["real"]
    )

print("Datos de prueba cargados exitosamente.")
