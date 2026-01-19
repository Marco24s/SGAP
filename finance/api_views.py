from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from core.models import EstructuraProgramatica
import json

@require_POST
@login_required
def create_program(request):
    try:
        data = json.loads(request.body)
        codigo = data.get('codigo')
        descripcion = data.get('descripcion')
        
        if not codigo or not descripcion:
            return JsonResponse({'error': 'Faltan datos requeridos'}, status=400)
            
        # Nivel 1 = Programa
        prog = EstructuraProgramatica.objects.create(
            nivel=1,
            codigo=codigo,
            descripcion=descripcion
        )
        
        return JsonResponse({
            'id': prog.id,
            'label': str(prog),
            'message': 'Programa creado correctamente'
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
