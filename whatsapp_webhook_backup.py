import json
from datetime import datetime
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Usuario, Examen, Base

# ---------------- CONFIGURACIÓN ----------------
app = Flask(__name__)
engine = create_engine("sqlite:///data.db")
Session = sessionmaker(bind=engine)

MIN_DIA = 5
MAX_DIA = 30
MAX_AVISOS = 4
AVISOS_DEFAULT = [30, 20, 10, 5]

# ---------------- UTILIDADES ----------------
def normalizar_avisos(avisos):
    if not avisos:
        return AVISOS_DEFAULT
    try:
        avisos = [int(x) for x in avisos]
    except ValueError:
        return AVISOS_DEFAULT
    filtrados = sorted({d for d in avisos if MIN_DIA <= d <= MAX_DIA}, reverse=True)
    return filtrados[:MAX_AVISOS] if filtrados else AVISOS_DEFAULT

def pretty_examenes(usuario):
    lines = []
    for ex in usuario.examenes:
        avisos_str = ex.avisos if ex.avisos else f"(usa globales: {usuario.avisos_globales})"
        lines.append(f"- {ex.curso}: {ex.fecha} | avisos: {avisos_str}")
    return "\n".join(lines) if lines else "No tienes exámenes registrados."

def help_text():
    return (
        "📚 *Menú de configuración*\n\n"
        "Escribe uno de estos comandos:\n"
        "• *MENU* → ver este menú\n"
        "• *MIS EXAMENES* → lista tus exámenes\n"
        "• *SET GLOBALES 30 20 10 5* → define avisos globales (5–30 días, máx 4)\n"
        "• *USAR GLOBALES SI* o *USAR GLOBALES NO*\n"
        "• *SET CURSO <curso> 20 10 5* → avisos solo para ese curso\n"
        "• *AGREGAR EXAMEN <curso> <YYYY-MM-DD> [avisos...]*\n"
        "• *CAMBIAR FECHA <curso> <YYYY-MM-DD>*\n"
        "• *ELIMINAR EXAMEN <curso>*\n"
    )

# ---------------- WEBHOOK ----------------
@app.route("/whatsapp", methods=["POST"])
def whatsapp_webhook():
    session = Session()
    incoming = request.values.get("Body", "").strip()
    from_phone = request.values.get("From")  # formato: whatsapp:+51XXXXXXXXX
    resp = MessagingResponse()

    usuario = session.query(Usuario).filter_by(telefono=from_phone).first()
    if usuario is None:
        resp.message("No encuentro tu número en el sistema. Escríbenos para registrarte. 📩")
        return str(resp)

    if not incoming:
        resp.message("Envía *MENU* para ver tus opciones.")
        return str(resp)

    parts = incoming.split()
    cmd = parts[0].upper()

    # --- MENU
    if cmd in ("MENU", "AYUDA", "HELP"):
        resp.message(help_text())
        return str(resp)

    # --- MIS EXAMENES
    if incoming.upper().startswith("MIS EXAMENES"):
        lista = pretty_examenes(usuario)
        resp.message(f"🗓 *Tus exámenes:*\n{lista}")
        return str(resp)

    # --- SET GLOBALES
    if incoming.upper().startswith("SET GLOBALES"):
        valores = incoming.upper().replace("SET GLOBALES", "").strip().split()
        avisos = normalizar_avisos(valores)
        usuario.avisos_globales = ",".join(map(str, avisos))
        usuario.usar_globales = True
        session.commit()
        resp.message(f"✅ Avisos globales guardados: {avisos}")
        return str(resp)

    # --- USAR GLOBALES SI/NO
    if incoming.upper().startswith("USAR GLOBALES"):
        palabra = parts[-1].upper()
        if palabra in ("SI", "SÍ", "YES"):
            usuario.usar_globales = True
            session.commit()
            resp.message("✅ Activado: se usarán tus avisos globales.")
        elif palabra in ("NO", "N"):
            usuario.usar_globales = False
            session.commit()
            resp.message("✅ Desactivado: cada curso tendrá sus propios avisos.")
        else:
            resp.message("Escribe: *USAR GLOBALES SI* o *USAR GLOBALES NO*.")
        return str(resp)

    resp.message("No entendí tu mensaje. Escribe *MENU* para ver las opciones.")
    return str(resp)

@app.route("/", methods=["GET"])
def home():
    return "WhatsApp Academic Bot OK"

if __name__ == "__main__":
    print(f"[{datetime.now()}] Iniciando webhook Flask en http://127.0.0.1:5000 ...")
    app.run(host="0.0.0.0", port=5000, debug=True)
