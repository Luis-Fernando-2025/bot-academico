import json
from datetime import datetime, timedelta

# Cargar datos de estudiantes y exámenes
with open("data.json", "r", encoding="utf-8") as f:
    estudiantes = json.load(f)

hoy = datetime.today().date()
dias_a_simular = 30  # Próximos 30 días

print(f"=== Calendario de recordatorios (desde {hoy} hasta {hoy + timedelta(days=dias_a_simular)}) ===\n")

for estudiante in estudiantes:
    print(f"--- {estudiante['nombre']} ({estudiante['telefono']}) ---")
    for examen in estudiante["examenes"]:
        fecha_examen = datetime.strptime(examen["fecha"], "%Y-%m-%d").date()
        avisos = examen.get("avisos", [3, 2, 1])
        fechas_avisos = [
            (fecha_examen - timedelta(days=d)).isoformat()
            for d in avisos
            if (fecha_examen - timedelta(days=d)) >= hoy
        ]
        print(f"  {examen['curso']} ({fecha_examen}): avisos -> {', '.join(fechas_avisos) if fechas_avisos else 'Ninguno'}")
    print()
