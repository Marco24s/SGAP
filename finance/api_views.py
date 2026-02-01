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

from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET"])
def get_program_details(request, pk):
    try:
        prog = get_object_or_404(EstructuraProgramatica, pk=pk)
        # Split code 16.02 -> 16, 02
        parts = prog.codigo.split('.')
        programa = parts[0]
        subprograma = parts[1] if len(parts) > 1 else ""
        
        return JsonResponse({
            'id': prog.id,
            'programa': programa,
            'subprograma': subprograma,
            'descripcion': prog.descripcion
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_POST
def update_program(request, pk):
    try:
        prog = get_object_or_404(EstructuraProgramatica, pk=pk)
        data = json.loads(request.body)
        
        programa = data.get('programa')
        subprograma = data.get('subprograma')
        descripcion = data.get('descripcion')
        
        if not programa or not subprograma or not descripcion:
            return JsonResponse({'error': 'Faltan datos requeridos'}, status=400)
            
        codigo_completo = f"{programa}.{subprograma}"
        
        prog.codigo = codigo_completo
        prog.descripcion = descripcion
        prog.save()
        
        return JsonResponse({
            'id': prog.id,
            'label': str(prog),
            'message': 'Programa actualizado correctamente'
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
