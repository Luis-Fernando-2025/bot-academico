from app import enviar_recordatorios
from datetime import date, timedelta

# Día inicial de prueba
hoy = date(2025, 7, 25)

# Simulamos 10 días (del 25 de julio al 3 de agosto)
for i in range(10):
    dia = hoy + timedelta(days=i)
    print(f"\n=== Simulación para el {dia} ===")
    enviar_recordatorios(dia)
