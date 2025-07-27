from models import SessionLocal, Usuario, Examen

def merge_users(telefono):
    session = SessionLocal()

    # Normalizamos el formato del teléfono
    if not telefono.startswith("whatsapp:"):
        telefono = "whatsapp:" + telefono

    # Buscamos todos los usuarios con este teléfono
    usuarios = session.query(Usuario).filter(
        Usuario.telefono.like(f"%{telefono.replace('whatsapp:', '')}%")
    ).all()

    if len(usuarios) <= 1:
        print(f"No hay duplicados para {telefono}.")
        return

    print(f"Usuarios encontrados para {telefono}: {len(usuarios)}")

    # Tomamos el primer usuario como principal
    usuario_principal = usuarios[0]

    # Fusionamos exámenes de los otros usuarios
    for u in usuarios[1:]:
        print(f" - Fusionando exámenes de usuario ID {u.id}")
        for examen in u.examenes:
            examen.usuario_id = usuario_principal.id
        session.delete(u)

    # Normalizamos el número del usuario principal
    usuario_principal.telefono = telefono
    session.commit()
    session.close()
    print(f"Usuarios fusionados y normalizados para {telefono}.")

if __name__ == "__main__":
    numero = input("Número de teléfono a fusionar (ej: +51972552408): ").strip()
    merge_users(numero)
