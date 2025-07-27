from models import SessionLocal, Usuario, Examen, init_db

# Inicializa la BD por si acaso
init_db()
session = SessionLocal()

# Crear usuario ficticio con zona horaria de Madrid
usuario = Usuario(
    telefono="whatsapp:+34123456789",  # Número ficticio
    avisos_globales="30,20,10,5",
    usar_globales=True,
    timezone="Europe/Madrid"
)
session.add(usuario)
session.commit()

# Crear examen para este usuario
examen = Examen(
    curso="Matemáticas",
    fecha="2025-08-15",
    avisos="30,20,10,5",
    usuario_id=usuario.id
)
session.add(examen)
session.commit()

print("Usuario de Madrid y examen creados correctamente.")
session.close()
