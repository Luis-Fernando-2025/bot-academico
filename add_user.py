from models import SessionLocal, Usuario, Examen
from sqlalchemy.orm import joinedload

def pedir_avisos(usuario_avisos):
    while True:
        avisos_input = input(
            "Días de aviso antes del examen (ej: 30,20,10,5) [Enter = por defecto]: "
        ).strip()
        if not avisos_input:
            return usuario_avisos

        try:
            avisos_list = [int(x) for x in avisos_input.split(",")]
            if any(a < 5 for a in avisos_list):
                print("⚠️ Todos los días de aviso deben ser 5 o más. Intenta de nuevo.")
                continue
            return ",".join(str(a) for a in avisos_list)
        except ValueError:
            print("❌ Entrada inválida. Usa solo números separados por comas.")

def registrar_examen(usuario):
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
        print(f"Examen de {curso} el {fecha} registrado correctamente.")

        continuar = input("¿Deseas registrar otro examen para este usuario? (s/n): ").strip().lower()
        if continuar != 's':
            break

def registrar_usuario_db(session, telefono, timezone, examenes):
    """
    Inserta un usuario con sus exámenes en la base de datos.
    - session: sesión SQLAlchemy.
    - telefono: string (ejemplo: whatsapp:+51999999999).
    - timezone: zona horaria (ejemplo: America/Lima).
    - examenes: lista de diccionarios [{curso: "Matemáticas", fecha: "2025-08-10", avisos: "30,10,5"}].
    """
    if not telefono.startswith("whatsapp:"):
        telefono = "whatsapp:" + telefono

    # Verificar si el usuario ya existe
    usuario = session.query(Usuario).filter_by(telefono=telefono).first()

    if not usuario:
        # Si no existe, crear un nuevo usuario
        usuario = Usuario(telefono=telefono, timezone=timezone)
        session.add(usuario)
        session.flush()  # Para asignar un ID antes de agregar exámenes

    # Añadir los exámenes al usuario (sin duplicados)
    for ex in examenes:
        nuevo_examen = Examen(
            curso=ex["curso"],
            fecha=ex["fecha"],
            avisos=ex.get("avisos", "30,10,5")
        )
        usuario.examenes.append(nuevo_examen)

    session.commit()
    return usuario

def main():
    session = SessionLocal()
    telefono = input("\n=== REGISTRO DE USUARIO ===\nNúmero de WhatsApp (con formato internacional, ej: whatsapp:+51999999999): ").strip()
    if not telefono.startswith("whatsapp:"):
        telefono = "whatsapp:" + telefono

    usuario = session.query(Usuario).options(joinedload(Usuario.examenes)).filter_by(telefono=telefono).first()

    if usuario:
        print(f"\nUsuario {telefono} ya existe con {len(usuario.examenes)} examen(es).")
        registrar_examen(usuario)
    else:
        timezone = input("Zona horaria (ej: America/Lima, Europe/Madrid): ").strip() or "America/Lima"
        usuario = Usuario(telefono=telefono, timezone=timezone)
        session.add(usuario)
        print(f"Usuario {telefono} creado con zona horaria {timezone}.")
        registrar_examen(usuario)

    session.commit()
    print("\n¡Registro completado!")
    session.close()

if __name__ == "__main__":
    main()
