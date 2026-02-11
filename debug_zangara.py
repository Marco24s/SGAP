from logistica.models import Personal, Asignacion, Prenda, TipoPrenda, Dotacion

try:
    zangara = Personal.objects.get(apellido__icontains='Zangara', nombre__icontains='Eugenio')
    print(f'Personal found: {zangara}, ID: {zangara.id}')
except Personal.DoesNotExist:
    print('Personal Zangara not found')
    zangara = None

if zangara:
    # Check Asignaciones
    asignaciones = zangara.asignaciones.all()
    print(f'\nTotal Asignaciones: {asignaciones.count()}')
    for a in asignaciones:
        print(f'  - Asignacion ID: {a.id}, Prenda: {a.prenda} (ID: {a.prenda.id}), TipoPrenda: {a.prenda.tipo_prenda}, Estado Asig: {a.activo}')
        if a.prenda.tipo_prenda:
            print(f'    -> TipoPrenda ID: {a.prenda.tipo_prenda.id}, Nombre: {a.prenda.tipo_prenda.nombre}')
        else:
            print(f'    -> [WARNING] Prenda has NO TipoPrenda linked!')

    # Check Dotacion Requirements
    print(f'\nDotacion Requirements for Rol: {zangara.rol}')
    dotacion = Dotacion.objects.filter(rol=zangara.rol)
    for d in dotacion:
        print(f'  - Requires: {d.tipo_prenda.nombre} (ID: {d.tipo_prenda.id}), Qty: {d.cantidad}')

    # Check specific "Buzo de Vuelo"
    buzo_tipo = TipoPrenda.objects.filter(nombre__icontains='Buzo de Vuelo').first()
    if buzo_tipo:
        print(f'\nChecking specific Type "Buzo de Vuelo" (ID: {buzo_tipo.id})')
        assigned_buzos = asignaciones.filter(prenda__tipo_prenda=buzo_tipo, activo=True)
        print(f'  - Assigned active Buzos found for Zangara: {assigned_buzos.count()}')
    else:
        print('\n[WARNING] TipoPrenda "Buzo de Vuelo" not found in DB')
