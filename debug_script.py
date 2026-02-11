from django.conf import settings
import os
import django
from logistica.models import Personal, Asignacion, Prenda, TipoPrenda, Dotacion

def run():
    print("Debug Script Started")
    # 1. Find the person
    try:
        zangara = Personal.objects.filter(apellido__icontains='Zangara').first()
        if not zangara:
            print("Zangara not found")
            return
        
        print(f"Checking assignments for: {zangara}")
        
        # 2. Check Dotacion Requirements for his Role
        print(f"\nRole: {zangara.rol}")
        dotacion_reqs = Dotacion.objects.filter(rol=zangara.rol)
        print(f"Dotacion Requirements ({dotacion_reqs.count()}):")
        
        buzo_req = None
        for req in dotacion_reqs:
            print(f"  - Requires: {req.tipo_prenda.nombre} (ID: {req.tipo_prenda.id}) Qty: {req.cantidad}")
            if "buzo" in req.tipo_prenda.nombre.lower() and "vuelo" in req.tipo_prenda.nombre.lower():
                buzo_req = req
        
        if not buzo_req:
            print("[ERROR] No 'Buzo de Vuelo' requirement found for this role!")
        
        # 3. Check Assignments
        print(f"\nAssignments for {zangara}:")
        asignaciones = Asignacion.objects.filter(personal=zangara, activo=True)
        print(f"Found {asignaciones.count()} active assignments.")
        
        for a in asignaciones:
            prenda = a.prenda
            tipo = prenda.tipo_prenda
            tipo_id = tipo.id if tipo else "None"
            tipo_nombre = tipo.nombre if tipo else "None"
            print(f"  - Asignacion ID: {a.id}")
            print(f"    Prenda: {prenda} (ID: {prenda.id})")
            print(f"    Tipo Prenda: {tipo_nombre} (ID: {tipo_id})")
            
            if buzo_req:
                print(f"    Matches Requirement ID {buzo_req.tipo_prenda.id}? {'YES' if tipo_id == buzo_req.tipo_prenda.id else 'NO'}")

    except Exception as e:
        print(f"Error during execution: {e}")

if __name__ == "__main__":
    run()
