from datetime import datetime
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from models import SessionLocal, Usuario, Examen, init_db

# ---------------- CONFIG ----------------
MIN_DIA = 5
MAX_DIA = 30
MAX_AVISOS = 4
AVISOS_DEFAULT = [30, 20, 10, 5]

app = Flask(__name__)
init_db()

# ---------------- Utils ----------------
def normalizar_avisos(avisos):
    if not avisos:
        return AVISOS_DEFAULT
    try:
        avisos = [int(x) for x in avisos]
    except ValueError:
        return AVISOS_DEFAULT
    filtrados = sorted({d for d in avisos if MIN_DIA <= d <= MAX_DIA}, reverse=True)
    return filtrados[:MAX_AVISOS] if filtrados else AVISOS_DEFAULT

def avisos_to_list(avisos_str):
    if not avisos_str:
        return []
    return [int(x) for x in avisos_str.split(",") if x.strip().isdigit()]

def avisos_to_str(lst):
    return ",".join(map(str, lst))

def pretty_examenes(usuario: Usuario):
    if not usuario.examenes:
        return "No tienes exámenes registrados."
    lines = []
    for ex in usuario.examenes:
        avisos = avisos_to_list(ex.avisos)
        if (not avisos) and usuario.usar_globales:
            avisos_str = f"(usa globales: {usuario.avisos_globales})"
        else:
            avisos_str = str(avisos if avisos else AVISOS_DEFAULT)
        lines.append(f"- {ex.curso}: {ex.fecha} | avisos: {avisos_str}")
    return "\n".join(lines)

def help_text():
    return (
        "📚 *Menú de configuración*\n\n"
        "• *MENU* → ver este menú\n"
        "• *MIS EXAMENES* → lista tus exámenes\n"
        "• *SET GLOBALES 30 20 10 5* → define avisos globales (5–30 días, máx 4)\n"
        "• *USAR GLOBALES SI* o *USAR GLOBALES NO*\n"
        "• *SET CURSO <curso> 20 10 5* → avisos solo para ese curso\n"
        "• *AGREGAR EXAMEN <curso> <YYYY-MM-DD> [avisos...]*\n"
        "• *CAMBIAR FECHA <curso> <YYYY-MM-DD>*\n"
        "• *ELIMINAR EXAMEN <curso>*\n"
    )

# ---------------- Webhook ----------------
@app.route("/whatsapp", methods=["POST"])
def whatsapp_webhook():
    session = SessionLocal()
    incoming = request.values.get("Body", "").strip()
    from_phone = request.values.get("From")  # formato: whatsapp:+51XXXXXXXXX
    resp = MessagingResponse()

    # buscar/crear usuario
    usuario = session.query(Usuario).filter_by(telefono=from_phone).first()
    if usuario is None:
        usuario = Usuario(
            telefono=from_phone,
            avisos_globales=avisos_to_str(AVISOS_DEFAULT),
            usar_globales=True
        )
        session.add(usuario)
        session.commit()
        resp.message("¡Hola! Te acabo de registrar. Escribe *MENU* para ver las opciones. 📲")
        session.close()
        return str(resp)

    if not incoming:
        resp.message("Envía *MENU* para ver tus opciones.")
        session.close()
        return str(resp)

    parts = incoming.split()
    cmd = parts[0].upper()

    # --- MENU
    if cmd in ("MENU", "AYUDA", "HELP"):
        resp.message(help_text())
        session.close()
        return str(resp)

    # --- MIS EXAMENES
    if incoming.upper().startswith("MIS EXAMENES"):
        lista = pretty_examenes(usuario)
        resp.message(f"🗓 *Tus exámenes:*\n{lista}")
        session.close()
        return str(resp)

    # --- SET GLOBALES
    if incoming.upper().startswith("SET GLOBALES"):
        try:
            valores = incoming.upper().replace("SET GLOBALES", "").strip().split()
            avisos = normalizar_avisos(valores)
            usuario.avisos_globales = avisos_to_str(avisos)
            usuario.usar_globales = True
            session.commit()
            resp.message(f"✅ Avisos globales guardados: {avisos}\nSe aplicarán a todos tus cursos.")
        except Exception as e:
            resp.message(f"❌ Error procesando: {e}")
        session.close()
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
        session.close()
        return str(resp)

    # --- SET CURSO <curso> d1 d2 d3 d4
    if incoming.upper().startswith("SET CURSO"):
        try:
            resto = incoming[len("SET CURSO"):].strip()
            tokens = resto.split()
            curso_tokens, dias_tokens = [], []
            for t in tokens:
                if t.isdigit():
                    dias_tokens.append(t)
                else:
                    curso_tokens.append(t)

            curso = " ".join(curso_tokens).strip()
            avisos = normalizar_avisos(dias_tokens)

            ex = session.query(Examen).filter_by(usuario_id=usuario.id, curso=curso).first()
            if ex is None:
                resp.message(f"❌ No encontré el curso '{curso}'.")
                session.close()
                return str(resp)

            ex.avisos = avisos_to_str(avisos)
            usuario.usar_globales = False
            session.commit()
            resp.message(f"✅ Avisos del curso *{curso}* actualizados a: {avisos}")
        except Exception as e:
            resp.message(f"❌ Error procesando SET CURSO: {e}")
        session.close()
        return str(resp)

    # --- AGREGAR EXAMEN <curso> <fecha> [avisos...]
    if incoming.upper().startswith("AGREGAR EXAMEN"):
        try:
            resto = incoming[len("AGREGAR EXAMEN"):].strip()
            tokens = resto.split()
            if len(tokens) < 2:
                resp.message("Formato: AGREGAR EXAMEN <curso> <YYYY-MM-DD> [avisos...]")
                session.close()
                return str(resp)

            fecha_idx = None
            for i, t in enumerate(tokens):
                if len(t) == 10 and t.count("-") == 2:
                    fecha_idx = i
                    break
            if fecha_idx is None:
                resp.message("Falta la fecha. Usa formato: YYYY-MM-DD")
                session.close()
                return str(resp)

            curso = " ".join(tokens[:fecha_idx])
            fecha = tokens[fecha_idx]
            dias_tokens = tokens[fecha_idx + 1:]
            avisos = normalizar_avisos(dias_tokens) if dias_tokens else []

            existente = session.query(Examen).filter_by(usuario_id=usuario.id, curso=curso).first()
            if existente:
                resp.message(f"❌ Ya existe un examen para el curso '{curso}'. Usa CAMBIAR FECHA o SET CURSO.")
                session.close()
                return str(resp)

            nuevo = Examen(
                curso=curso,
                fecha=fecha,
                avisos=avisos_to_str(avisos)
            )
            usuario.examenes.append(nuevo)
            session.commit()
            resp.message(f"✅ Examen agregado: *{curso}* el {fecha} (avisos: {avisos if avisos else '(usará globales/default)'})")
        except Exception as e:
            resp.message(f"❌ Error procesando AGREGAR EXAMEN: {e}")
        session.close()
        return str(resp)

    # --- CAMBIAR FECHA <curso> <YYYY-MM-DD>
    if incoming.upper().startswith("CAMBIAR FECHA"):
        try:
            resto = incoming[len("CAMBIAR FECHA"):].strip()
            tokens = resto.split()
            if len(tokens) < 2:
                resp.message("Formato: CAMBIAR FECHA <curso> <YYYY-MM-DD>")
                session.close()
                return str(resp)

            fecha = tokens[-1]
            curso = " ".join(tokens[:-1])

            ex = session.query(Examen).filter_by(usuario_id=usuario.id, curso=curso).first()
            if ex is None:
                resp.message(f"❌ No encontré el curso '{curso}'.")
                session.close()
                return str(resp)

            ex.fecha = fecha
            session.commit()
            resp.message(f"✅ Fecha actualizada para *{curso}*: {fecha}")
        except Exception as e:
            resp.message(f"❌ Error procesando CAMBIAR FECHA: {e}")
        session.close()
        return str(resp)

    # --- ELIMINAR EXAMEN <curso>
    if incoming.upper().startswith("ELIMINAR EXAMEN"):
        try:
            curso = incoming[len("ELIMINAR EXAMEN"):].strip()
            ex = session.query(Examen).filter_by(usuario_id=usuario.id, curso=curso).first()
            if ex is None:
                resp.message(f"❌ No encontré el curso '{curso}'.")
                session.close()
                return str(resp)

            session.delete(ex)
            session.commit()
            resp.message(f"✅ Examen eliminado: *{curso}*")
        except Exception as e:
            resp.message(f"❌ Error procesando ELIMINAR EXAMEN: {e}")
        session.close()
        return str(resp)

    resp.message("No entendí tu mensaje. Escribe *MENU* para ver las opciones.")
    session.close()
    return str(resp)

@app.route("/", methods=["GET"])
def home():
    return "WhatsApp Academic Bot OK"

if __name__ == "__main__":
    print(f"[{datetime.now()}] Iniciando webhook Flask en http://127.0.0.1:5000 ...")
    app.run(host="0.0.0.0", port=5000, debug=True)
