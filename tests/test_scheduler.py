# tests/test_scheduler.py
import sys
import os

# Asegurar que la raíz del proyecto esté en sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scheduler import generar_mensajes_recordatorio


def test_generar_mensajes_recordatorio():
    examenes = [
        {"curso": "Matemáticas", "fecha": "2025-08-10", "avisos": "30,10,5"},
        {"curso": "Física", "fecha": "2025-08-15", "avisos": "20,5"}
    ]
    mensajes = generar_mensajes_recordatorio(examenes, dias_faltantes=30)

    # Debe haber al menos un mensaje con 'Matemáticas'
    assert any("Matemáticas" in m for m in mensajes)
