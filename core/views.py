from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

# Create your views here.

@login_required
def logout_view(request):
    logout(request)
    return redirect('core:login')

def landing_logistica(request):
    return render(request, 'core/landing_logistica.html')

@login_required
def control_view(request):
    from .models import IncisoControl, GastoOperativo
    
    # Get cuatrigrama filter (default to COAN)
    cuatrigrama_actual = request.GET.get('q', 'COAN')
    
    # Filter by cuatrigrama, or get all if 'COAN' is selected
    if cuatrigrama_actual == 'COAN':
        incisos = IncisoControl.objects.all().prefetch_related('historial')
    else:
        incisos = IncisoControl.objects.filter(cuatrigrama=cuatrigrama_actual).prefetch_related('historial')
    
    # Get all GastoOperativo objects (no filtering by cuatrigrama for now)
    gastos = GastoOperativo.objects.all()
    
    # Calculate totals for IncisoControl
    total_respaldo = sum(i.respaldo for i in incisos)
    total_asignacion = sum(i.asignacion for i in incisos)
    total_dev_com = sum(i.dev_com for i in incisos)
    total_saldo = sum(i.saldo for i in incisos)
    total_falta_asignar = sum(i.falta_asignar for i in incisos)

    # The original code had GastoOperativo calculations, but the provided snippet removes them.
    # Keeping the GastoOperativo query for now, but its calculations are removed from context.
    gastos = GastoOperativo.objects.all() 
    
    # If GastoOperativo totals are still needed, they should be re-added here.
    # For now, following the provided snippet which removes them from the context.
    total_emav_estimado = sum(g.importe_estimado for g in gastos)
    total_emav_real = sum(g.importe_real for g in gastos)
    total_emav_saldo = total_emav_estimado - total_emav_real

    context = {
        'incisos': incisos,
        'cuatrigrama_actual': cuatrigrama_actual,
        'total_respaldo': total_respaldo,
        'total_asignacion': total_asignacion,
        'total_dev_com': total_dev_com,
        'total_saldo': total_saldo,
        'total_falta_asignar': total_falta_asignar,
        # The following were in the original context but removed by the provided snippet.
        # Re-adding them to maintain consistency if they are used in the template,
        # but the snippet explicitly removed their calculation from the main totals.
        'gastos': gastos,
        'total_emav_estimado': total_emav_estimado,
        'total_emav_real': total_emav_real,
        'total_emav_saldo': total_emav_saldo,
    }
    return render(request, 'core/control.html', context)

# --- Vistas CRUD para Control ---

from .forms import IncisoControlForm, GastoOperativoForm
from .models import IncisoControl, GastoOperativo, HistorialInciso


@login_required
def inciso_create(request):
    initial_data = {}
    if 'q' in request.GET:
        initial_data['cuatrigrama'] = request.GET['q']
        
    if request.method == 'POST':
        form = IncisoControlForm(request.POST)
        if form.is_valid():
            inciso = form.save(commit=False)
            if 'q' in request.GET:
                inciso.cuatrigrama = request.GET['q']
            inciso.save()
            
            # Guardar historial inicial si hay nota
            if inciso.nota:
                HistorialInciso.objects.create(inciso=inciso, nota=inciso.nota)
                
            return redirect(reverse('core:control') + f"?q={inciso.cuatrigrama}")
    else:
        form = IncisoControlForm(initial=initial_data)
    return render(request, 'core/form_base.html', {'form': form, 'title': f'Nuevo Inciso ({initial_data.get("cuatrigrama", "")})'})

@login_required
def inciso_edit(request, pk):
    inciso = get_object_or_404(IncisoControl, pk=pk)
    if request.method == 'POST':
        form = IncisoControlForm(request.POST, instance=inciso)
        if form.is_valid():
            inciso = form.save(commit=False)
            
            # Verificar si cambió la nota para guardar historial
            # O guardar siempre que se edite, para tener traza (como pidió el usuario "registro de los cambios")
            # Vamos a guardar si hay nota, o si la nota cambió.
            # Para simplificar y cumplir con "registro de los cambios", guardamos un hito en el historial.
            if inciso.nota:
                 HistorialInciso.objects.create(inciso=inciso, nota=inciso.nota)
            
            inciso.save()
            return redirect(reverse('core:control') + f"?q={inciso.cuatrigrama}")
    else:
        form = IncisoControlForm(instance=inciso)
    return render(request, 'core/form_base.html', {'form': form, 'title': f'Editar Inciso ({inciso.cuatrigrama})'})

@login_required
def gasto_create(request):
    if request.method == 'POST':
        form = GastoOperativoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('core:control')
    else:
        form = GastoOperativoForm()
    return render(request, 'core/form_base.html', {'form': form, 'title': 'Nuevo Gasto Operativo'})

@login_required
def gasto_edit(request, pk):
    gasto = get_object_or_404(GastoOperativo, pk=pk)
    if request.method == 'POST':
        form = GastoOperativoForm(request.POST, instance=gasto)
        if form.is_valid():
            form.save()
            return redirect('core:control')
    else:
        form = GastoOperativoForm(instance=gasto)
    return render(request, 'core/form_base.html', {'form': form, 'title': 'Editar Gasto Operativo'})

def control_placeholder_view(request):
    return render(request, 'core/control_placeholder.html')
