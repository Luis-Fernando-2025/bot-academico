# add_user.py
import argparse
from typing import List, Dict
import pytz
from models import SessionLocal, Usuario, Examen
from sqlalchemy.orm import joinedload

DEFAULT_AVISOS = "30,20,10,5"
DEFAULT_TZ = "America/Lima"


# ----------------- Helpers -----------------
def validar_timezone(tz: str) -> str:
    if tz in pytz.all_timezones:
        return tz
    raise ValueError(f"Zona horaria inválida: {tz}. Revisa https://en.wikipedia.org/wiki/List_of_tz_database_time_zones")


def validar_avisos(cadena: str) -> str:
    try:
        avisos = [int(x) for x in cadena.split(",")]
    except Exception:
        raise ValueError("Formato de avisos inválido. Usa números separados por comas. Ej: 30,20,10,5")
    if any(a < 5 for a in avisos):
        raise ValueError("Todos los días de aviso deben ser >= 5")
    return ",".join(str(a) for a in avisos)


def pedir_avisos(usuario_avisos):
    while True:
        avisos_input = input(
            f"Días de aviso antes del examen (ej: 30,20,10,5) [Enter = {usuario_avisos or DEFAULT_AVISOS}]: "
        ).strip()

        if not avisos_input:
            return usuario_avisos or DEFAULT_AVISOS

        try:
            return validar_avisos(avisos_input)
        except ValueError as e:
            print(f"❌ {e}")


def parsear_examenes_args(exam_args: List[str]) -> List[Dict]:
    """
    Cada --examen se pasa como:  Curso|YYYY-MM-DD|30,20,10,5
    El tramo de avisos es opcional. Ej:
      --examen "Matemáticas|2025-08-10|30,10,5"
      --examen "Física|2025-09-01"
    """
    examenes = []
    for raw in exam_args:
        partes = [p.strip() for p in raw.split("|")]
        if len(partes) < 2:
            raise ValueError(f"Formato inválido para --examen: {raw}. Usa: Curso|YYYY-MM-DD|30,20,10,5")
        curso = partes[0]
        fecha = partes[1]
        avisos = DEFAULT_AVISOS if len(partes) < 3 or not partes[2] else validar_avisos(partes[2])
        examenes.append({"curso": curso, "fecha": fecha, "avisos": avisos})
    return examenes


# --------------- Lógica DB -----------------
def registrar_examen_interactivo(usuario):
    while True:
        curso = input("\nNombre del curso (ej: Física): ").strip()
        fecha = input("Fecha del examen (formato YYYY-MM-DD): ").strip()
        avisos = pedir_avisos(usuario.avisos_globales)

        nuevo_examen = Examen(
            curso=curso,
            fecha=fecha,
            avisos=avisos
        )
        usuario.examenes.append(nuevo_examen)
        print(f"✅ Examen de {curso} el {fecha} registrado correctamente.")

        continuar = input("¿Deseas registrar otro examen para este usuario? (s/n): ").strip().lower()
        if continuar != 's':
            break


def registrar_usuario_db(session, telefono, timezone, examenes):
    """
    Inserta un usuario con sus exámenes en la base de datos.
    Devuelve datos planos para evitar DetachedInstanceError.
    """
    telefono_norm = telefono if telefono.startswith("whatsapp:") else "whatsapp:" + telefono

    usuario = session.query(Usuario).filter_by(telefono=telefono_norm).first()

    if not usuario:
        usuario = Usuario(telefono=telefono_norm, timezone=timezone)
        session.add(usuario)
        session.flush()

    for ex in examenes:
        nuevo_examen = Examen(
            curso=ex["curso"],
            fecha=ex["fecha"],
            avisos=ex.get("avisos", DEFAULT_AVISOS)
        )
        usuario.examenes.append(nuevo_examen)

    session.commit()

    return {"telefono": telefono_norm, "nuevos_examenes": len(examenes)}


# --------------- CLI / Main -----------------
def main_cli():
    parser = argparse.ArgumentParser(description="Registrar usuarios y exámenes (modo CLI o interactivo).")
    parser.add_argument("--telefono", help="Número de WhatsApp en formato internacional (ej: +51999999999)")
    parser.add_argument("--timezone", help=f"Zona horaria del usuario (ej: {DEFAULT_TZ})", default=DEFAULT_TZ)
    parser.add_argument(
        "--examen",
        action="append",
        help='Puedes repetir --examen varias veces. Formato: "Curso|YYYY-MM-DD|30,20,10,5" (avisos opcional).'
    )
    args = parser.parse_args()

    if not args.telefono:
        return main_interactivo()

    try:
        tz = validar_timezone(args.timezone)
    except ValueError as e:
        print(f"❌ {e}")
        return

    if not args.examen:
        print("❌ Debes pasar al menos un --examen en modo CLI.")
        return

    try:
        examenes = parsear_examenes_args(args.examen)
    except ValueError as e:
        print(f"❌ {e}")
        return

    session = SessionLocal()
    result = registrar_usuario_db(session, args.telefono, tz, examenes)
    session.close()
    print(f"✅ Usuario {result['telefono']} actualizado/creado con {result['nuevos_examenes']} examen(es).")


def main_interactivo():
    session = SessionLocal()
    telefono = input("\n=== REGISTRO DE USUARIO ===\nNúmero de WhatsApp (con formato internacional, ej: whatsapp:+51999999999): ").strip()
    if not telefono.startswith("whatsapp:"):
        telefono = "whatsapp:" + telefono

    usuario = session.query(Usuario).options(joinedload(Usuario.examenes)).filter_by(telefono=telefono).first()

    if usuario:
        print(f"\nUsuario {telefono} ya existe con {len(usuario.examenes)} examen(es).")
        registrar_examen_interactivo(usuario)
    else:
        timezone = input(f"Zona horaria (ej: {DEFAULT_TZ}, Europe/Madrid): ").strip() or DEFAULT_TZ
        try:
            timezone = validar_timezone(timezone)
        except ValueError as e:
            print(f"❌ {e}")
            session.close()
            return

        usuario = Usuario(telefono=telefono, timezone=timezone)
        session.add(usuario)
        print(f"✅ Usuario {telefono} creado con zona horaria {timezone}.")
        registrar_examen_interactivo(usuario)

    session.commit()
    print("\n¡Registro completado!")
    session.close()


if __name__ == "__main__":
    main_cli()
