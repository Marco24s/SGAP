from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from core.models import EstructuraProgramatica
import json

@require_POST
def create_program(request):
    try:
        data = json.loads(request.body)
        programa = data.get('programa')
        subprograma = data.get('subprograma')
        descripcion = data.get('descripcion')
        
        if not programa or not subprograma or not descripcion:
            return JsonResponse({'error': 'Faltan datos requeridos'}, status=400)
            
        # Format code as Program.Subprogram (e.g., 16.02)
        codigo_completo = f"{programa}.{subprograma}"
        
        # Nivel 1 = Programa (Simplification for now, usually Program is Level 1, Subprogram Level 2)
        # Storing as single Level 1 entry for simple dropdown selection
        prog = EstructuraProgramatica.objects.create(
            nivel=1,
            codigo=codigo_completo,
            descripcion=descripcion
        )
        
        return JsonResponse({
            'id': prog.id,
            'label': str(prog),
            'message': 'Programa creado correctamente'
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
