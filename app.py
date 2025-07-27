import os
import json
import schedule
import time
import random
from datetime import datetime, date
from pathlib import Path
from dotenv import load_dotenv

# ================== CONFIG ==================
DRY_RUN = True  # True => Simulación (no envía). False => Enviar mensajes reales.
SENT_LOG_PATH = Path("sent_log.json")  # Log para evitar duplicados diarios
HORARIOS = ["09:00", "15:00"]  # Horas programadas
AVISOS_DEFAULT = [30, 10, 5]  # Si no hay avisos válidos
MIN_DIA = 5
MAX_DIA = 30
MAX_AVISOS = 4
# ============================================

# ========== CARGA DE ENTORNO Y PROVEEDOR ==========
load_dotenv()
TWILIO_FROM = "whatsapp:+14155238886"
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")

try:
    from twilio.rest import Client
    client = Client(account_sid, auth_token)
    TWILIO_ACTIVO = True
except Exception:
    TWILIO_ACTIVO = False
    print("[AVISO] Twilio no está disponible. Solo modo simulación.")

# ================== DATOS ==================
CITAS = [
    "La motivación nos impulsa a comenzar, el hábito nos permite continuar. – Jim Ryun",
    "No cuentes los días, haz que los días cuenten. – Muhammad Ali",
    "Cree en ti y todo será posible. – Theodore Roosevelt",
    "El éxito es 1% inspiración y 99% transpiración. – Thomas Edison"
]

IMAGENES = [
    "https://i.imgur.com/Fu7bAfk.jpeg",
    "https://i.imgur.com/1c8fQn1.jpeg",
    "https://i.imgur.com/3yq8v8b.jpeg"
]

# ================== FUNCIONES AUXILIARES ==================
def load_json(path, default):
    try:
        if Path(path).exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"[{datetime.now()}] Error leyendo {path}: {e}")
    return default

def save_json(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[{datetime.now()}] Error guardando {path}: {e}")

def ya_enviado_hoy(log, student_name, course, exam_date, hoy):
    key = f"{student_name}|{course}|{exam_date}|{hoy.isoformat()}"
    return key in log

def marcar_enviado(log, student_name, course, exam_date, hoy):
    key = f"{student_name}|{course}|{exam_date}|{hoy.isoformat()}"
    log[key] = True

def normalizar_avisos(avisos):
    """ Mantiene solo valores entre 5 y 30, máximo 4, sin duplicados, orden desc. """
    if not avisos:
        return AVISOS_DEFAULT
    filtrados = sorted(
        {d for d in avisos if MIN_DIA <= d <= MAX_DIA},
        reverse=True
    )
    if not filtrados:
        return AVISOS_DEFAULT
    return filtrados[:MAX_AVISOS]

def obtener_avisos(estudiante, examen):
    usar_globales = estudiante.get("usar_globales", False)
    if usar_globales:
        return normalizar_avisos(estudiante.get("avisos_globales", []))
    else:
        return normalizar_avisos(examen.get("avisos", []))

# ================== INTERFAZ DE MENSAJERÍA ==================
def enviar_mensaje(to, body, media_url=None):
    """Interfaz única para enviar mensajes, independientemente del proveedor."""
    if DRY_RUN or not TWILIO_ACTIVO:
        print(f"[{datetime.now()}] (SIMULADO) -> {to}: {body}")
        return "SIMULADO"

    try:
        msg = client.messages.create(
            from_=TWILIO_FROM,
            body=body,
            media_url=media_url or [],
            to=to
        )
        print(f"[{datetime.now()}] Enviado a {to} (SID: {msg.sid})")
        return msg.sid
    except Exception as e:
        print(f"[{datetime.now()}] Error enviando a {to}: {e}")
        return None

# ================== LÓGICA PRINCIPAL ==================
def enviar_recordatorios(simulated_today: date | None = None):
    estudiantes = load_json("data.json", default=[])
    sent_log = load_json(SENT_LOG_PATH, default={})

    hoy = simulated_today or datetime.today().date()

    for estudiante in estudiantes:
        for examen in estudiante["examenes"]:
            fecha_examen = datetime.strptime(examen["fecha"], "%Y-%m-%d").date()
            dias_restantes = (fecha_examen - hoy).days

            avisos = obtener_avisos(estudiante, examen)

            if dias_restantes in avisos:
                if ya_enviado_hoy(sent_log, estudiante["nombre"], examen["curso"], examen["fecha"], hoy):
                    continue

                cita = random.choice(CITAS)
                imagen = random.choice(IMAGENES)
                cuerpo = (
                    f"Hola {estudiante['nombre']}! "
                    f"Tu examen de {examen['curso']} es en {dias_restantes} día(s). "
                    f"¡Es hora de prepararte! 💪\n"
                    f"Frase inspiradora: {cita}"
                )

                enviar_mensaje(estudiante["telefono"], cuerpo, media_url=[imagen])
                marcar_enviado(sent_log, estudiante["nombre"], examen["curso"], examen["fecha"], hoy)

    save_json(SENT_LOG_PATH, sent_log)

def main():
    print(f"Arrancando bot académico. DRY_RUN = {DRY_RUN}. Hoy: {datetime.today().date()}")
    enviar_recordatorios()

    for h in HORARIOS:
        schedule.every().day.at(h).do(enviar_recordatorios)

    print(f"Horarios activos: {', '.join(HORARIOS)}")
    while True:
        schedule.run_pending()
        time.sleep(30)

if __name__ == "__main__":
    main()
