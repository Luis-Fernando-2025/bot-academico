from models import SessionLocal, Usuario

session = SessionLocal()

usuario = session.query(Usuario).filter(Usuario.telefono == "+51972552408").first()
if usuario:
    usuario.timezone = "America/Lima"
    session.commit()
    print(f"Zona horaria actualizada para {usuario.telefono} -> {usuario.timezone}")
else:
    print("Usuario no encontrado.")

session.close()
