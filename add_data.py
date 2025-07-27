from models import SessionLocal, Usuario, Examen

def agregar_datos():
    session = SessionLocal()

    nuevo_usuario = Usuario(
        telefono="whatsapp:+51972552408",
        avisos_globales="30,20,10,5",
        usar_globales=True,
        timezone="America/Lima"  # <- Zona horaria del usuario
    )

    examen = Examen(
        curso="Física",
        fecha="2025-08-15",
        avisos="30,20,10,5"
    )

    nuevo_usuario.examenes.append(examen)
    session.add(nuevo_usuario)
    session.commit()
    session.close()

    print("Usuario y examen agregados correctamente.")

if __name__ == "__main__":
    agregar_datos()
