from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Personal, Prenda, Asignacion, Movimiento, Dotacion, TipoPrenda
from django.utils import timezone
from django.contrib import messages

from .forms import PersonalForm, PrendaForm, AsignacionForm, TipoPrendaForm, DotacionForm

@login_required
def index(request):
    """Main Dashboard for Logistica"""
    total_personal = Personal.objects.filter(estado=True).count()
    total_prendas = Prenda.objects.count()
    prendas_disponibles = Prenda.objects.filter(estado='deposito').count()
    asignaciones_activas = Asignacion.objects.filter(fecha_devolucion__isnull=True).count()
    
    context = {
        'total_personal': total_personal,
        'total_prendas': total_prendas,
        'prendas_disponibles': prendas_disponibles,
        'asignaciones_activas': asignaciones_activas,
    }
    return render(request, 'logistica/index.html', context)

# --- Personal Views ---
@login_required
def personal_list(request):
    personal = Personal.objects.all()
    return render(request, 'logistica/personal_list.html', {'personal': personal})

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
                usuario=request.user.username,
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
                usuario=request.user.username,
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
                usuario=request.user.username,
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
            asignados = Asignacion.objects.filter(
                personal=persona,
                activo=True,
                prenda__tipo_prenda=item_req.tipo_prenda
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
