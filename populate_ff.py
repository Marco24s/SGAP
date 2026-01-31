from core.models import FuenteFinanciamiento

data = [
    {"codigo": "11", "descripcion": "Tesoro Nacional"},
    {"codigo": "13", "descripcion": "Recursos Específicos"},
]

for item in data:
    obj, created = FuenteFinanciamiento.objects.get_or_create(
        codigo=item['codigo'],
        defaults={'descripcion': item['descripcion']}
    )
    if created:
        print(f"Created: {obj}")
    else:
        print(f"Already exists: {obj}")

print("Done.")
