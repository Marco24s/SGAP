from django.shortcuts import render, get_object_or_404, redirect
from .models import Credito, Asignacion
from core.models import ClasificadorGasto, UnidadComponente, EstructuraProgramatica
from django.contrib import messages
from django.utils import timezone
from .forms import CreditoForm

def nuevo_credito(request):
    if request.method == "POST":
        form = CreditoForm(request.POST)
        if form.is_valid():
            credito = form.save(commit=False)
            credito.estado = 'VIGENTE' # Default state
            credito.save()
            messages.success(request, "Nuevo Crédito registrado correctamente.")
            return redirect('finance:lista_creditos')
    else:
        form = CreditoForm()
    return render(request, 'finance/nuevo_credito.html', {'form': form})

def lista_creditos(request):
    creditos = Credito.objects.filter(estado='VIGENTE')
    return render(request, 'finance/lista_creditos.html', {'creditos': creditos})

def distribuir_credito(request, credito_id):
    credito = get_object_or_404(Credito, pk=credito_id)
    asignaciones = credito.asignaciones.all()
    
    # Context data for form
    incisos = ClasificadorGasto.objects.filter(nivel=1)
    uuccs = UnidadComponente.objects.all()
    obras = EstructuraProgramatica.objects.filter(nivel=4) # Assuming 4 is Obra
    
    if request.method == "POST":
        uucc_id = request.POST.get('uucc')
        try:
            uucc = UnidadComponente.objects.get(pk=uucc_id)
            
            # Iterate over all POST keys to find allocations
            # Expected format: amount_INCISOID, detail_INCISOID (optional)
            for key, value in request.POST.items():
                if key.startswith('monto_') and value:
                    if key == 'monto_combined_23':
                        continue
                    inciso_id = key.split('_')[1]
                    monto = float(value)
                    
                    # Logic:
                    # 1. Check if 'detalle_INCISOID' exists
                    selected_classifier_id = request.POST.get(f'detalle_{inciso_id}')
                    if selected_classifier_id:
                        clasificador = ClasificadorGasto.objects.get(pk=selected_classifier_id)
                    else:
                        clasificador = ClasificadorGasto.objects.get(pk=inciso_id)
                        
                    # Check Obstruction/Constraints (Inciso 4 requires Obra)
                    obra_id = request.POST.get(f'obra_{inciso_id}')
                    obra = None
                    if obra_id:
                        obra = EstructuraProgramatica.objects.get(pk=obra_id)

                    # Create Asignacion
                    Asignacion.objects.create(
                        uucc=uucc,
                        credito_origen=credito,
                        clasificador_gasto=clasificador,
                        monto=monto,
                        trimestre=credito.trimestre, # Inherit from Credit
                        obra=obra
                    )
            
            # Special Handling for Combined 2 & 3
            if request.POST.get('monto_combined_23'):
                monto_23 = float(request.POST.get('monto_combined_23'))
                # Assign to Inciso 2 (Bienes) as primary container for "Funcionamiento"
                # Searching for Inciso 2 by code strictly
                inciso_2 = ClasificadorGasto.objects.filter(nivel=1, codigo='2').first()
                if inciso_2:
                    Asignacion.objects.create(
                        uucc=uucc,
                        credito_origen=credito,
                        clasificador_gasto=inciso_2,
                        monto=monto_23,
                        trimestre=credito.trimestre
                    )
            
            messages.success(request, f"Asignación registrada exitosamente para {uucc.codigo}.")
            return redirect('finance:distribuir_credito', credito_id=credito.id)

        except Exception as e:
            messages.error(request, f"Error al asignar: {e}")
            
    context = {
        'credito': credito,
        'asignaciones': asignaciones,
        'incisos': incisos,
        'uuccs': uuccs,
        'obras': obras
    }
    return render(request, 'finance/distribuir.html', context)

def load_children_classifiers(request):
    padre_id = request.GET.get('padre_id')
    if not padre_id:
        return render(request, 'finance/partials/classifier_options.html', {'options': []})
    
    # If padre is Inciso 2 (Consumo), rule says Global.
    # But usually we might still want to show children if they exist, or just stop.
    # User rule: "Inciso 2 -> Distribute Global".
    # Logic:
    padre = ClasificadorGasto.objects.get(pk=padre_id)
    
    # Specific Rule enforcement for dropdown generation
    if padre.nivel == 1 and padre.codigo == '2':
        # Don't show children, allowing selection of the Inciso itself is implied by the parent logic?
        # Or returns empty options implies "Leaf reached".
        children = [] 
    else:
        children = ClasificadorGasto.objects.filter(padre_id=padre_id)
        
from .models import Credito, Asignacion, ModificacionPresupuestaria
from .forms import ModificacionForm
from django.db import transaction

# ... existing views ...

def lista_modificaciones(request):
    modificaciones = ModificacionPresupuestaria.objects.all().order_by('-fecha_solicitud')
    return render(request, 'finance/lista_modificaciones.html', {'modificaciones': modificaciones})

def nueva_modificacion(request):
    if request.method == "POST":
        form = ModificacionForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                # Logic: Deduct from Origin, Add to Destination IF Approved
                modificacion = form.save(commit=False)
                
                # Auto-approve logic based on rule (Same Program)
                # Form valid determines type, let's verify logic in View or Form? 
                # Keeping it simple: If 'APROBADO', execute movement immediately.
                
                if modificacion.estado == 'APROBADO':
                    modificacion.origen.monto -= modificacion.monto
                    modificacion.origen.save()
                    modificacion.destino.monto += modificacion.monto
                    modificacion.destino.save()
                    modificacion.fecha_aprobacion = timezone.now()
                
                modificacion.save()
                messages.success(request, f"Modificación {modificacion.get_tipo_display()} registrada correctamente.")
                return redirect('finance:modificaciones')
    else:
        form = ModificacionForm()
    
    return render(request, 'finance/nueva_modificacion.html', {'form': form})

from .forms import AutorizacionCargoForm
from .models import AutorizacionCargo

def lista_autorizaciones(request):
    autorizaciones = AutorizacionCargo.objects.filter(activo=True)
    return render(request, 'finance/lista_autorizaciones.html', {'autorizaciones': autorizaciones})

def nueva_autorizacion(request):
    if request.method == "POST":
        form = AutorizacionCargoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Autorización de Cargo generada correctamente.")
            return redirect('finance:lista_autorizaciones')
    else:
        form = AutorizacionCargoForm()
    return render(request, 'finance/nueva_autorizacion.html', {'form': form})

from .models import Compromiso
def simular_ejecucion(request):
    """
    Tool for AA.PP to simulate execution by UU.CC for testing purposes.
    """
    if request.method == "POST":
        asignacion_id = request.POST.get('asignacion')
        monto = request.POST.get('monto')
        if asignacion_id and monto:
            try:
                asignacion = Asignacion.objects.get(pk=asignacion_id)
                Compromiso.objects.create(
                    asignacion=asignacion,
                    monto=monto,
                    concepto="Gasto Simulado Dashboard"
                )
                messages.success(request, f"Ejecución de ${monto} registrada para {asignacion.uucc}.")
            except Exception as e:
                messages.error(request, f"Error: {e}")
        return redirect('finance:simular_ejecucion')
        
    # Get all asignaciones to pick from
    asignaciones_qs = Asignacion.objects.select_related('uucc', 'clasificador_gasto').all()
    
    # Pre-format options to avoid template tag issues
    asignaciones_list = []
    for a in asignaciones_qs:
        monto_fmt = f"{a.monto:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
        label = f"{a.uucc.codigo} - {a.clasificador_gasto.codigo} (Disp: ${monto_fmt})"
        asignaciones_list.append({
            'id': a.id,
            'label': label
        })

    return render(request, 'finance/simular_ejecucion.html', {'asignaciones': asignaciones_list})
