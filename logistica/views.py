from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Personal, Prenda, Asignacion, Movimiento, Dotacion, TipoPrenda, ROLES_CHOICES
from django.utils import timezone
from django.contrib import messages
from django.db.models import Q
from datetime import date, timedelta

from .forms import PersonalForm, PrendaForm, AsignacionForm, TipoPrendaForm, DotacionForm

def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, [31,
        29 if year % 4 == 0 and not year % 400 == 0 else 28,
        31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month-1])
    return date(year, month, day)

@login_required
def necesidades_compra(request):
    anio_actual = timezone.now().year
    anio_proximo = anio_actual + 1
    fin_anio_proximo = date(anio_proximo, 12, 31)
    
    personal_activo = Personal.objects.filter(estado=True)
    necesidades_detalle = []
    
    # Mapping simple para talles
    def get_talle(personal, tipo_nombre):
        nombre_lower = tipo_nombre.lower()
        if 'casco' in nombre_lower: return personal.talle_casco
        if 'guante' in nombre_lower: return personal.talle_guantes
        if 'over' in nombre_lower or 'mono' in nombre_lower or 'buzo' in nombre_lower: return personal.talle_overall
        if 'bota' in nombre_lower or 'calzado' in nombre_lower: return personal.talle_botas
        return 'N/A' # Default si no matchea nada especifico

    for p in personal_activo:
        # Obtener dotacion requerida para su rol
        dotacion = Dotacion.objects.filter(rol=p.rol)
        
        for item in dotacion:
            tipo = item.tipo_prenda
            talle = get_talle(p, tipo.nombre) or "Sin Talle"
            
            # Buscar asignacion activa
            asignacion = Asignacion.objects.filter(
                personal=p, 
                prenda__tipo_prenda=tipo, 
                activo=True
            ).order_by('-fecha_entrega').first()
            
            necesidad = None
            
            if not asignacion:
                # Faltante detectado
                necesidad = {
                    'personal': p,
                    'tipo': tipo.nombre,
                    'talle': talle,
                    'motivo': 'Faltante',
                    'fecha_limite': timezone.now().date(),
                    'sort_date': timezone.now().date()
                }
            else:
                # Calcular vencimiento
                meses_duracion = item.renovacion_int
                fecha_vencimiento = add_months(asignacion.fecha_entrega, meses_duracion)
                
                if fecha_vencimiento <= fin_anio_proximo:
                    necesidad = {
                        'personal': p,
                        'tipo': tipo.nombre,
                        'talle': talle,
                        'motivo': 'Vencimiento',
                        'fecha_limite': fecha_vencimiento,
                        'sort_date': fecha_vencimiento
                    }
            
            if necesidad:
                necesidades_detalle.append(necesidad)
    
    # Agrupar para resumen (Pivot Table: Tipo vs Talles)
    # 1. Collect all unique talles and types
    all_talles = set()
    resumen_matrix = {} # { 'Tipo': { 'term_people': { 'Talle': [list of names] }, 'total_people': [list of names] } }

    for n in necesidades_detalle:
        tipo = n['tipo']
        talle = n['talle']
        persona_str = f"{n['personal'].grado} {n['personal'].apellido} {n['personal'].nombre}"
        
        all_talles.add(talle)
        
        if tipo not in resumen_matrix:
            resumen_matrix[tipo] = {'term_people': {}, 'total_people': []}
        
        if talle not in resumen_matrix[tipo]['term_people']:
            resumen_matrix[tipo]['term_people'][talle] = []
            
        resumen_matrix[tipo]['term_people'][talle].append(persona_str)
        resumen_matrix[tipo]['total_people'].append(persona_str)

    # 2. Sort Talles (Try to sort numerically if possible, otherwise alphabetic)
    def sort_talle_key(t):
        try:
            return (0, int(t))
        except ValueError:
            return (1, t)
            
    sorted_talles = sorted(list(all_talles), key=sort_talle_key)
    
    # 3. Sort Tipos
    sorted_tipos = sorted(resumen_matrix.keys())
    
    # 4. Build Rows for Template
    pivot_rows = []
    for tipo in sorted_tipos:
        # Get total count and people
        total_people = resumen_matrix[tipo]['total_people']
        
        row_data = {
            'tipo': tipo,
            'counts': [], # Will store dicts: { 'count': N, 'people': [list] }
            'total': len(total_people),
            'total_people': total_people
        }
        for talle in sorted_talles:
            people_list = resumen_matrix[tipo]['term_people'].get(talle, [])
            count = len(people_list)
            
            cell_data = {
                'count': count if count > 0 else '-',
                'people': people_list,
                'talle': talle
            }
            row_data['counts'].append(cell_data)
            
        pivot_rows.append(row_data)

    # Ordenar detalle por fecha para la lista inferior
    necesidades_detalle.sort(key=lambda x: x['sort_date'])

    return render(request, 'logistica/necesidades_compra.html', {
        'pivot_rows': pivot_rows,
        'sorted_talles': sorted_talles,
        'necesidades_detalle': necesidades_detalle,
        'anio_proximo': anio_proximo
    })

@login_required
def index(request):
    """Main Dashboard for Logistica"""
    # Dynamic Filter Logic
    filter_type = request.GET.get('filter_type')
    filter_value = request.GET.get('filter_value')
    
    p_base_qs = Personal.objects.all()

    # Define Hierarchies
    JERARQUIAS = {
        'Oficiales': ['CF', 'CC', 'TN', 'TF', 'TC', 'GU'],
        'Suboficiales': ['SM', 'SP', 'SI', 'SS', 'CP', 'CI', 'CS'],
        'Marinería': ['MR', 'M2'],
        'Civiles': ['CV'],
    }
    
    if filter_type and filter_value:
        if filter_type == 'unidad':
            p_base_qs = p_base_qs.filter(unidad=filter_value)
        elif filter_type == 'grado':
            p_base_qs = p_base_qs.filter(grado=filter_value)
        elif filter_type == 'jerarquia':
            if filter_value in JERARQUIAS:
                p_base_qs = p_base_qs.filter(grado__in=JERARQUIAS[filter_value])

    # Personal Stats (By Role)
    roles_stats = []
    grand_total = 0
    grand_activo = 0
    grand_baja = 0

    for codigo, nombre in ROLES_CHOICES:
        # Filter by role on top of the base queryset (which might be filtered by unit/grado)
        p_qs = p_base_qs.filter(rol=codigo)
        
        total = p_qs.count()
        activos = p_qs.filter(estado=True).count()
        baja = p_qs.filter(estado=False).count()
        
        roles_stats.append({
            'label': nombre,
            'codigo': codigo, # Added for filtering links
            'total': total,
            'activos': activos,
            'baja': baja,
        })
        
        grand_total += total
        # Accumulate for grand total from the specific role counts to ensure consistency
        grand_activo += activos
        grand_baja += baja

    grand_total_stats = {
        'total': grand_total,
        'activos': grand_activo,
        'baja': grand_baja
    }
    
    # Get units for the filter dropdown
    unidades = [u[0] for u in PersonalForm.UNIDAD_CHOICES]
    grados = Personal.GRADOS_CHOICES
    
    # Prenda Stats
    total_prendas = Prenda.objects.count()
    prendas_disponibles = Prenda.objects.filter(estado='deposito').count()
    asignaciones_activas = Asignacion.objects.filter(fecha_devolucion__isnull=True).count()
    
    context = {
        'roles_stats': roles_stats,
        'grand_total_stats': grand_total_stats,
        'total_prendas': total_prendas,
        'prendas_disponibles': prendas_disponibles,
        'asignaciones_activas': asignaciones_activas,
        'unidades': unidades,
        'grados': grados,
        'jerarquias': list(JERARQUIAS.keys()),
        'filter_type': filter_type,
        'filter_value': filter_value,
    }
    return render(request, 'logistica/index.html', context)

# --- Personal Views ---
@login_required
def personal_list(request):
    personal = Personal.objects.all()
    
    # Filter by Role
    rol_filtro = request.GET.get('rol', '')
    if rol_filtro:
        personal = personal.filter(rol=rol_filtro)

    # Dynamic Filters (from Dashboard)
    filter_type = request.GET.get('filter_type', '')
    filter_value = request.GET.get('filter_value', '')
    
    # Define Hierarchies (Should ideally be in a shared constant or service, but keeping here for now)
    JERARQUIAS = {
        'Oficiales': ['CF', 'CC', 'TN', 'TF', 'TC', 'GU'],
        'Suboficiales': ['SM', 'SP', 'SI', 'SS', 'CP', 'CI', 'CS'],
        'Marinería': ['MR', 'M2'],
        'Civiles': ['CV'],
    }

    if filter_type and filter_value:
        if filter_type == 'unidad':
            personal = personal.filter(unidad=filter_value)
        elif filter_type == 'grado':
            personal = personal.filter(grado=filter_value)
        elif filter_type == 'jerarquia':
            if filter_value in JERARQUIAS:
                personal = personal.filter(grado__in=JERARQUIAS[filter_value])
        
            if filter_value in JERARQUIAS:
                personal = personal.filter(grado__in=JERARQUIAS[filter_value])

    # Sorting Logic
    order_by = request.GET.get('order_by', 'apellido') # Default sort
    direction = request.GET.get('direction', 'asc')

    allowed_sort_fields = ['legajo', 'grado', 'apellido', 'unidad', 'rol', 'estado']
    
    if order_by in allowed_sort_fields:
        if direction == 'desc':
            personal = personal.order_by(f'-{order_by}')
        else:
            personal = personal.order_by(order_by)
        
    context = {
        'personal': personal,
        'unidades': [u[0] for u in PersonalForm.UNIDAD_CHOICES],
        'grados': Personal.GRADOS_CHOICES,
        'jerarquias': list(JERARQUIAS.keys()),
        'filter_type': filter_type,
        'filter_value': filter_value,
        'rol_filtro': rol_filtro,
        'order_by': order_by,
        'direction': direction,
    }
    return render(request, 'logistica/personal_list.html', context)

@login_required
def personal_create(request):
    if request.method == 'POST':
        form = PersonalForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Personal registrado exitosamente.")
            return redirect('logistica:personal_list')
    else:
        form = PersonalForm()
    return render(request, 'logistica/personal_form.html', {'form': form})

@login_required
def personal_update(request, pk):
    personal = get_object_or_404(Personal, pk=pk)
    if request.method == 'POST':
        form = PersonalForm(request.POST, instance=personal)
        if form.is_valid():
            form.save()
            messages.success(request, "Datos actualizados correctamente.")
            return redirect('logistica:personal_list')
    else:
        form = PersonalForm(instance=personal)
    return render(request, 'logistica/personal_form.html', {'form': form, 'update': True})

@login_required
def personal_delete(request, pk):
    personal = get_object_or_404(Personal, pk=pk)
    if request.method == 'POST':
        personal.delete()
        messages.success(request, "Personal eliminado correctamente.")
        return redirect('logistica:personal_list')
    return redirect('logistica:personal_list')

# --- Prenda Views ---
@login_required
def prenda_list(request):
    prendas = Prenda.objects.all()
    return render(request, 'logistica/prenda_list.html', {'prendas': prendas})

@login_required
def prenda_create(request):
    if request.method == 'POST':
        form = PrendaForm(request.POST)
        if form.is_valid():
            prenda = form.save()
            # Registrar movimiento de Alta
            Movimiento.objects.create(
                prenda=prenda,
                tipo='alta',
                usuario=request.user,
                observaciones=f"Alta inicial: {prenda.descripcion}"
            )
            messages.success(request, "Prenda registrada exitosamente.")
            return redirect('logistica:prenda_list')
    else:
        form = PrendaForm()
    return render(request, 'logistica/prenda_form.html', {'form': form})

@login_required
def prenda_update(request, pk):
    prenda = get_object_or_404(Prenda, pk=pk)
    if request.method == 'POST':
        form = PrendaForm(request.POST, instance=prenda)
        if form.is_valid():
            # Check if status changed to log movement? For now just save.
            form.save()
            Movimiento.objects.create(
                prenda=prenda,
                tipo='modificacion',
                usuario=request.user,
                observaciones=f"Modificación de datos: {prenda.codigo_interno}"
            )
            messages.success(request, "Prenda actualizada correctamente.")
            return redirect('logistica:prenda_list')
    else:
        form = PrendaForm(instance=prenda)
    return render(request, 'logistica/prenda_form.html', {'form': form, 'update': True})

# --- Asignacion Views ---
@login_required
def asignacion_list(request):
    asignaciones = Asignacion.objects.filter(fecha_devolucion__isnull=True)
    return render(request, 'logistica/asignacion_list.html', {'asignaciones': asignaciones})

@login_required
def asignacion_create(request):
    if request.method == 'POST':
        form = AsignacionForm(request.POST)
        if form.is_valid():
            asignacion = form.save(commit=False)
            prenda = asignacion.prenda
            
            # Verificar si la prenda ya está asignada (aunque el filtro del form ayuda, es doble seguridad)
            if prenda.estado != 'deposito':
                messages.error(request, f"La prenda {prenda} no está en depósito.")
                return render(request, 'logistica/asignacion_form.html', {'form': form})

            asignacion.save()
            
            # Actualizar estado de la prenda
            prenda.estado = 'asignada'
            prenda.save()

            # Registrar Movimiento
            Movimiento.objects.create(
                prenda=prenda,
                tipo='asignacion',
                usuario=request.user,
                observaciones=f"Asignada a {asignacion.personal}"
            )

            messages.success(request, "Asignación creada exitosamente.")
            return redirect('logistica:asignacion_list')
    else:
        form = AsignacionForm()
    return render(request, 'logistica/asignacion_form.html', {'form': form})

@login_required
def asignacion_return(request, pk):
    asignacion = get_object_or_404(Asignacion, pk=pk)
    if request.method == 'POST':
        asignacion.fecha_devolucion = timezone.now()
        asignacion.activo = False
        asignacion.save()
        
        # Update Prenda status
        prenda = asignacion.prenda
        prenda.estado = 'deposito' 
        prenda.save()
        
        # Registrar Movimiento
        Movimiento.objects.create(
            prenda=prenda,
            tipo='devolucion',
            usuario=request.user.username,
            observaciones=f"Devolución de {asignacion.personal}"
        )

        messages.success(request, f"Prenda {prenda} devuelta exitosamente.")
        return redirect('logistica:asignacion_list')
    
    return render(request, 'logistica/asignacion_confirm_return.html', {'asignacion': asignacion})

@login_required
def estado_dotacion(request):
    personal_list = Personal.objects.filter(estado=True)
    reporte = []

    for persona in personal_list:
        # Get requirements for this person's role
        dotacion_requerida = Dotacion.objects.filter(rol=persona.rol)
        estado_persona = {
            'personal': persona,
            'items': [],
            'todo_ok': True
        }

        for item_req in dotacion_requerida:
            # Count assigned items of this type
            # Use explicit ID filtering for robustness
            asignados = Asignacion.objects.filter(
                personal=persona,
                activo=True,
                prenda__tipo_prenda_id=item_req.tipo_prenda.id
            ).count()

            estado_item = {
                'tipo': item_req.tipo_prenda.nombre,
                'requerido': item_req.cantidad,
                'asignado': asignados,
                'estado': 'ok' if asignados >= item_req.cantidad else 'falta'
            }
            
            if estado_item['estado'] == 'falta':
                estado_persona['todo_ok'] = False
            
            estado_persona['items'].append(estado_item)
        
        if dotacion_requerida.exists(): # Only add if there are requirements
             reporte.append(estado_persona)

    return render(request, 'logistica/estado_dotacion.html', {'reporte': reporte})

# --- Tipo Prenda Management ---
@login_required
def tipo_prenda_list(request):
    tipos = TipoPrenda.objects.all()
    return render(request, 'logistica/tipo_prenda_list.html', {'tipos': tipos})

@login_required
def tipo_prenda_create(request):
    if request.method == 'POST':
        form = TipoPrendaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Tipo de prenda creado exitosamente.")
            return redirect('logistica:tipo_prenda_list')
    else:
        form = TipoPrendaForm()
    return render(request, 'logistica/tipo_prenda_form.html', {'form': form})

@login_required
def tipo_prenda_update(request, pk):
    tipo = get_object_or_404(TipoPrenda, pk=pk)
    if request.method == 'POST':
        form = TipoPrendaForm(request.POST, instance=tipo)
        if form.is_valid():
            form.save()
            messages.success(request, "Tipo de prenda actualizado exitosamente.")
            return redirect('logistica:tipo_prenda_list')
    else:
        form = TipoPrendaForm(instance=tipo)
    return render(request, 'logistica/tipo_prenda_form.html', {'form': form, 'update': True})

@login_required
def tipo_prenda_delete(request, pk):
    tipo = get_object_or_404(TipoPrenda, pk=pk)
    if request.method == 'POST':
        tipo.delete()
        messages.success(request, "Tipo de prenda eliminado exitosamente.")
        return redirect('logistica:tipo_prenda_list')
    # If GET, redirect back to list or show confirmation page (here just redirect for safety)
    return redirect('logistica:tipo_prenda_list')


# --- Dotacion Rules Management ---
@login_required
def dotacion_list(request):
    dotaciones = Dotacion.objects.order_by('rol')
    return render(request, 'logistica/dotacion_list.html', {'dotaciones': dotaciones})

@login_required
def dotacion_create(request):
    if request.method == 'POST':
        form = DotacionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Regla de dotación creada exitosamente.")
            return redirect('logistica:dotacion_list')
    else:
        form = DotacionForm()
    return render(request, 'logistica/dotacion_form.html', {'form': form})

@login_required
def dotacion_update(request, pk):
    dotacion = get_object_or_404(Dotacion, pk=pk)
    if request.method == 'POST':
        form = DotacionForm(request.POST, instance=dotacion)
        if form.is_valid():
            form.save()
            messages.success(request, "Regla de dotación actualizada exitosamente.")
            return redirect('logistica:dotacion_list')
    else:
        form = DotacionForm(instance=dotacion)
    return render(request, 'logistica/dotacion_form.html', {'form': form, 'update': True})

@login_required
def dotacion_delete(request, pk):
    dotacion = get_object_or_404(Dotacion, pk=pk)
    if request.method == 'POST':
        dotacion.delete()
        messages.success(request, "Regla de dotación eliminada exitosamente.")
        return redirect('logistica:dotacion_list')
    return redirect('logistica:dotacion_list')
