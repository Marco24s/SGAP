from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Credito, Asignacion
from core.models import ClasificadorGasto, UnidadComponente, EstructuraProgramatica
from django.contrib import messages
from django.utils import timezone
from .forms import CreditoForm

@login_required
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
    return render(request, 'finance/nuevo_credito.html', {'form': form, 'title': 'Cargar Nuevo Crédito Presupuestario'})

@login_required
def editar_credito(request, credito_id):
    credito = get_object_or_404(Credito, id=credito_id)
    if request.method == "POST":
        form = CreditoForm(request.POST, instance=credito)
        if form.is_valid():
            form.save()
            messages.success(request, "Crédito actualizado correctamente.")
            return redirect('finance:lista_creditos')
    else:
        form = CreditoForm(instance=credito)
    return render(request, 'finance/nuevo_credito.html', {'form': form, 'title': 'Editar Crédito Presupuestario', 'is_edit': True})

@login_required
def eliminar_credito(request, credito_id):
    credito = get_object_or_404(Credito, id=credito_id)
    if request.method == "POST":
        credito.delete()
        messages.success(request, "Crédito eliminado correctamente.")
        return redirect('finance:lista_creditos')
    
    return render(request, 'finance/confirmar_eliminar.html', {'credito': credito})

@login_required
def lista_creditos(request):
    from collections import defaultdict
    
    def fmt_currency(value):
        """Format currency as 1.000.000"""
        return f"{value:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    creditos = Credito.objects.filter(estado='VIGENTE').select_related('programa', 'fuente').order_by('-fecha_creacion')
    
    # Check grouping mode
    group_by = request.GET.get('group_by', 'default')
    
    # Group credits
    # Structure: {'total': 0, 'cuota': 0, 'creditos': [], 'seen_budgets': set()}
    # seen_budgets tracks (programa, fuente, inciso, anio) to avoid double counting Annual Totals
    grupos = defaultdict(lambda: {'total': 0, 'cuota': 0, 'creditos': [], 'seen_budgets': set()})
    
    for credito in creditos:
        if group_by == 'ff':
            key = (credito.fuente.id,)
        elif group_by == 'programa':
            key = (credito.programa.id,)
        elif group_by == 'inciso':
            key = (credito.inciso,)
        else: # default
            key = (credito.programa.id, credito.anio, credito.trimestre, credito.fuente.id, credito.inciso, credito.principal)
            
        # Unique identifier for the "Annual Budget Line"
        budget_key = (credito.programa.id, credito.fuente.id, credito.inciso, credito.anio, credito.principal)
        
        # Only add to TOTAL if this budget line hasn't been counted for this group yet
        if budget_key not in grupos[key]['seen_budgets']:
            grupos[key]['total'] += credito.monto_total
            grupos[key]['seen_budgets'].add(budget_key)
            
        # Always add to CUOTA (since that's cumulative cash released)
        grupos[key]['cuota'] += credito.monto_cuota
        
        grupos[key]['creditos'].append({
            'id': credito.id,
            'monto': fmt_currency(credito.monto_total),
            'cuota': fmt_currency(credito.monto_cuota),
            'monto_raw': credito.monto_total,
            'recibido': credito.recibido,
            'fecha': credito.fecha_creacion.strftime('%d/%m/%Y %H:%M')
        })
        
        # Populate representative data based on grouping
        if group_by == 'ff':
            grupos[key]['fuente'] = credito.fuente
        elif group_by == 'programa':
            grupos[key]['programa'] = credito.programa
        elif group_by == 'inciso':
            grupos[key]['inciso'] = credito.inciso
        else:
            grupos[key]['programa'] = credito.programa
            grupos[key]['anio'] = credito.anio
            grupos[key]['trimestre'] = credito.trimestre
            grupos[key]['fuente'] = credito.fuente
            grupos[key]['inciso'] = credito.inciso
            grupos[key]['principal'] = credito.principal
    
    # Convert to list for template
    creditos_agrupados = []
    for key, data in grupos.items():
        item = {
            'total': fmt_currency(data['total']),
            'cuota': fmt_currency(data['cuota']),
            'creditos': data['creditos'],
            'is_recibido': data['creditos'][0]['recibido'] if data['creditos'] else True,
            'count': len(data['creditos'])
        }
        
        # Fill specific fields based on mode
        if group_by == 'ff':
            item['fuente'] = data['fuente']
        elif group_by == 'programa':
            item['programa'] = data['programa']
        elif group_by == 'inciso':
            item['inciso'] = data['inciso']
        else:
            item['programa'] = data['programa']
            item['anio'] = str(data['anio'])
            item['trimestre'] = data['trimestre']
            item['fuente'] = data['fuente']
            item['inciso'] = data['inciso']
            item['principal'] = data.get('principal', '')
            
        creditos_agrupados.append(item)
    
    # Sort Logic
    if group_by == 'ff':
        creditos_agrupados.sort(key=lambda x: str(x['fuente']))
    elif group_by == 'programa':
        creditos_agrupados.sort(key=lambda x: str(x['programa']))
    elif group_by == 'inciso':
        creditos_agrupados.sort(key=lambda x: x['inciso'])
    else:
        creditos_agrupados.sort(key=lambda x: (x['anio'], x['trimestre'], str(x['programa']), x['inciso'], x['principal']))
    
    # Calculate Grand Total for display
    # Calculate Grand Total for display
    # Logic: Sum 'monto_total' (Annual Ceiling) only ONCE per unique budget line (Program+Source+Inciso+Year+Principal)
    grand_total = 0
    seen_budgets_global = set()
    
    for credito in creditos:
         budget_key = (credito.programa.id, credito.fuente.id, credito.inciso, credito.anio, credito.principal)
         if budget_key not in seen_budgets_global:
             grand_total += credito.monto_total
             seen_budgets_global.add(budget_key)
             
    grand_total_display = fmt_currency(grand_total)

    return render(request, 'finance/lista_creditos_v2.html', {
        'creditos_agrupados': creditos_agrupados, 
        'group_by': group_by,
        'grand_total': grand_total_display
    })

@login_required
def load_credit_history(request):
    from collections import defaultdict
    
    programa_id = request.GET.get('programa')
    anio = request.GET.get('anio')
    trimestre = request.GET.get('trimestre')
    fuente_id = request.GET.get('fuente')
    inciso = request.GET.get('inciso')
    principal = request.GET.get('principal')
    
    # Filter credits matching the criteria
    filters = {
        'estado': 'VIGENTE',
        'programa_id': programa_id,
        'anio': anio,
        'trimestre': trimestre,
        'fuente_id': fuente_id,
        'inciso': inciso
    }
    
    # Only filter by principal if explicitly passed (handle mixed legacy calls if any, though usually strings)
    if principal is not None:
        filters['principal'] = principal

    creditos = Credito.objects.filter(**filters).order_by('-fecha_creacion')

    def fmt_currency(value):
        return f"{value:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    creditos_data = []
    total = 0
    programa_nombre = ""
    fuente_nombre = ""
    
    for credito in creditos:
        # Capture names from first valid credit
        if not programa_nombre:
            programa_nombre = str(credito.programa)
        if not fuente_nombre:
            fuente_nombre = str(credito.fuente)
            
        total += credito.monto_total
        creditos_data.append({
            'id': credito.id,
            'monto': fmt_currency(credito.monto_cuota),
            'inciso': credito.inciso,
            'principal': credito.principal,
            'fecha': credito.fecha_creacion.strftime('%d/%m/%Y %H:%M')
        })
        
    context = {
        'creditos': creditos_data,
        'program': programa_nombre, # passed as simple string to avoid template accessing complex objects if not needed
        'programa': programa_nombre,
        'anio': str(anio) if anio else '',
        'trimestre': trimestre,
        'fuente': fuente_nombre,
        'final_total_display': fmt_currency(total)
    }
    print("DEBUG: Sending final_total_display:", context['final_total_display'])
    
    return render(request, 'finance/partials/history_modal.html', context)

@login_required
def eliminar_asignacion(request, asignacion_id):
    asignacion = get_object_or_404(Asignacion, pk=asignacion_id)
    credito_id = asignacion.credito_origen.id
    
    try:
        # Allowing GET for simple trash icon link, but ideally use form.
        asignacion.delete()
        messages.success(request, "Asignación eliminada correctamente.")

    except Exception as e:
         messages.error(request, f"No se puede eliminar la asignación: {e}")
         
    return redirect('finance:distribuir_credito', credito_id=credito_id)

@login_required
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
            
            # Retrieve inputs
            monto = float(request.POST.get('monto', 0))
            solicitud_gfh = request.POST.get('solicitud_gfh', '')
            asignacion_gfh = request.POST.get('asignacion_gfh', '')
            objeto = request.POST.get('objeto', '')

            if monto < 0:
                 raise ValueError("El monto asignado debe ser mayor a 0")
                 
            # Determine Clasificador based on Credit
            # Rule: We try to match the Credit's Inciso code to a ClasificadorGasto
            inciso_code = credito.inciso
            
            # Hotfix: Map '20' -> '2', '30' -> '3', etc. if they don't exist
            mapping = {'20': '2', '30': '3', '40': '4', '50': '5', '10': '1'}
            if inciso_code in mapping:
                inciso_code = mapping[inciso_code]

            clasificador = ClasificadorGasto.objects.filter(nivel=1, codigo=inciso_code).first()
            if not clasificador:
                raise ValueError(f"No se encontró un Clasificador válido para el Inciso {credito.inciso} (Buscado: {inciso_code})")

            # Check Obstruction/Constraints (Inciso 4 requires Obra)
            obra = None
            if credito.inciso == '4':
                obra_id = request.POST.get('obra')
                if not obra_id:
                     raise ValueError("Es obligatorio seleccionar una Obra para Inciso 4")
                obra = EstructuraProgramatica.objects.get(pk=obra_id)

            # Check if this is an update
            asignacion_id = request.POST.get('asignacion_id')
            if asignacion_id:
                asignacion = get_object_or_404(Asignacion, pk=asignacion_id)
                # Verify it belongs to this credit (security)
                if asignacion.credito_origen != credito:
                    raise ValueError("La asignación no corresponde a este crédito.")
                
                asignacion.uucc = uucc
                asignacion.monto = monto
                asignacion.solicitud_gfh = solicitud_gfh
                asignacion.asignacion_gfh = asignacion_gfh
                asignacion.objeto = objeto
                asignacion.obra = obra
                asignacion.save()
                messages.success(request, f"Asignación actualizada exitosamente para {uucc.codigo}.")
            else:
                # Create Asignacion
                Asignacion.objects.create(
                    uucc=uucc,
                    credito_origen=credito,
                    clasificador_gasto=clasificador,
                    monto=monto,
                    solicitud_gfh=solicitud_gfh,
                    asignacion_gfh=asignacion_gfh,
                    objeto=objeto,
                    trimestre=credito.trimestre, # Inherit from Credit
                    obra=obra
                )
                messages.success(request, f"Asignación registrada exitosamente para {uucc.codigo}.")

            return redirect('finance:distribuir_credito', credito_id=credito.id)

        except Exception as e:
            messages.error(request, f"Error al asignar: {e}")
            

    # Calculate "Saldo Parcial Asignado" requested by user
    # Logic: Sum of quotas (monto_cuota) for the same budget line (program, source, year, inciso)
    # ONLY if received=True
    related_credits = Credito.objects.filter(
        programa=credito.programa,
        fuente=credito.fuente,
        anio=credito.anio,
        inciso=credito.inciso
    )
    
    saldo_parcial_asignado = 0
    for c in related_credits:
        if c.recibido:
            saldo_parcial_asignado += c.monto_cuota

    # Calculate Total Distributed (Saldo Asignado)
    total_distribuido = credito.monto_total - credito.saldo_disponible

    context = {
        'credito': credito,
        'asignaciones': asignaciones,
        'incisos': incisos,
        'uuccs': uuccs,
        'obras': obras,
        'saldo_parcial_asignado': saldo_parcial_asignado,
        'total_distribuido': total_distribuido
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

@login_required
def lista_modificaciones(request):
    modificaciones = ModificacionPresupuestaria.objects.all().order_by('-fecha_solicitud')
    return render(request, 'finance/lista_modificaciones.html', {'modificaciones': modificaciones})

@login_required
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

@login_required
def lista_autorizaciones(request):
    autorizaciones = AutorizacionCargo.objects.filter(activo=True)
    return render(request, 'finance/lista_autorizaciones.html', {'autorizaciones': autorizaciones})

@login_required
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
@login_required
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
