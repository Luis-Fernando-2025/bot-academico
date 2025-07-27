# scheduler.py
import os
import argparse
import random
from datetime import datetime, date, timezone
import pytz
from dotenv import load_dotenv
from twilio.rest import Client
from models import SessionLocal, Usuario, Examen, init_db

# ---------------- CONFIG ----------------
DRY_RUN_DEFAULT = True
AVISOS_DEFAULT = [30, 20, 10, 5]
TWILIO_FROM_DEFAULT = "whatsapp:+14155238886"

CITAS = [
    "El éxito es la suma de pequeños esfuerzos repetidos cada día. – Robert Collier",
    "La disciplina es el puente entre metas y logros. – Jim Rohn",
    "Haz lo que debes hacer, aunque no quieras hacerlo. – Brian Tracy",
    "No dejes que el tiempo decida por ti, decide tú por el tiempo. – Anónimo"
]

def parse_avisos(cadena: str | None):
    if not cadena:
        return []
    return [int(x) for x in cadena.split(",") if x.strip().isdigit()]

def enviar_whatsapp(client, to, body, dry_run: bool):
    if dry_run:
        print(f"[SIMULADO] -> {to}: {body}")
        return "SIMULADO"
    try:
        msg = client.messages.create(
            from_=os.getenv("TWILIO_WHATSAPP_NUMBER", TWILIO_FROM_DEFAULT),
            body=body,
            to=to
        )
        print(f"[OK] Enviado a {to} (SID: {msg.sid})")
        return msg.sid
    except Exception as e:
        print(f"[ERROR] Enviando a {to}: {e}")
        return None

def generar_mensajes_recordatorio(examenes, dias_faltantes, hoy: date | None = None):
    if hoy is None:
        hoy = date.today()

    mensajes = []
    for ex in examenes:
        try:
            fecha_examen = datetime.strptime(ex["fecha"], "%Y-%m-%d").date()
        except ValueError:
            continue
        dias_restantes = (fecha_examen - hoy).days
        if dias_restantes == dias_faltantes:
            cita = random.choice(CITAS)
            mensajes.append(
                f"📢 *Recordatorio de examen*\n\n"
                f"Tu examen de *{ex['curso']}* es en *{dias_restantes}* día(s) "
                f"(fecha: {ex['fecha']}).\nFrase: {cita}"
            )
    return mensajes

def run_once(hoy: date, dry_run: bool, ignore_hour: bool):
    init_db()
    session = SessionLocal()

    load_dotenv()
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")

    client = None
    if not dry_run:
        if not account_sid or not auth_token:
            print("[ERROR] No hay credenciales Twilio en .env.")
            session.close()
            return
        client = Client(account_sid, auth_token)

    now_utc = datetime.now(timezone.utc)
    total_enviados = 0
    usuarios = session.query(Usuario).all()

    for u in usuarios:
        avisos_globales = parse_avisos(u.avisos_globales) or AVISOS_DEFAULT
        tz = pytz.timezone(u.timezone or "America/Lima")
        fecha_actual_usuario = hoy

        # Chequeo de hora local 08:00
        if not ignore_hour:
            hora_local = now_utc.astimezone(tz).hour
            if hora_local != 8:
                continue

        for ex in u.examenes:
            try:
                fecha_examen = datetime.strptime(ex.fecha, "%Y-%m-%d").date()
            except ValueError:
                print(f"[WARN] Fecha inválida para {u.telefono} - {ex.curso}: {ex.fecha}")
                continue

            dias_restantes = (fecha_examen - fecha_actual_usuario).days
            if dias_restantes < 0:
                continue

            avisos_locales = parse_avisos(ex.avisos)
            avisos = avisos_locales or avisos_globales

            if dias_restantes in avisos:
                cita = random.choice(CITAS)
                body = (
                    f"📢 *Recordatorio de examen*\n\n"
                    f"Hola! Tu examen de *{ex.curso}* es en *{dias_restantes}* día(s) "
                    f"(fecha: {ex.fecha}).\n\n"
                    f"Es un buen momento para organizar tu estudio. 💪\n"
                    f"Frase: {cita}"
                )
                enviar_whatsapp(client, u.telefono, body, dry_run)
                total_enviados += 1

    session.close()
    print(f"[INFO] Proceso terminado. Mensajes {'simulados' if dry_run else 'reales'} enviados: {total_enviados}")

def main():
    parser = argparse.ArgumentParser(description="Scheduler de recordatorios académicos.")
    parser.add_argument("--sim", help="Fecha simulada (YYYY-MM-DD).", default=None)
    parser.add_argument("--send", action="store_true", help="Enviar realmente por Twilio.")
    parser.add_argument("--ignore-hour", action="store_true", help="Ignorar el filtro de hora local 08:00.")
    args = parser.parse_args()

    hoy = date.today()
    if args.sim:
        hoy = datetime.strptime(args.sim, "%Y-%m-%d").date()

    dry_run = not args.send
    print(f"[INFO] Ejecutando scheduler. Hoy={hoy}  DRY_RUN={dry_run}  IGNORE_HOUR={args.ignore_hour}")
    run_once(hoy, dry_run, args.ignore_hour)

if __name__ == "__main__":
    main()
