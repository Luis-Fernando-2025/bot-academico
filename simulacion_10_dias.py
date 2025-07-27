from app import enviar_recordatorios
from datetime import date, timedelta

# Simularemos 10 días desde hoy
hoy = date.today()

print(f"=== Simulación de recordatorios para los próximos 10 días (desde {hoy}) ===\n")

for i in range(10):
    fecha_simulada = hoy + timedelta(days=i)
    print(f"\n=== Día simulado: {fecha_simulada} ===")
    enviar_recordatorios(fecha_simulada)
