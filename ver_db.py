from models import SessionLocal, Usuario, Examen

session = SessionLocal()

usuarios = session.query(Usuario).all()

print("=== USUARIOS Y EXÁMENES ===")
for u in usuarios:
    print(f"Usuario: {u.telefono}, avisos_globales: {u.avisos_globales}, usar_globales: {u.usar_globales}")
    for ex in u.examenes:
        print(f"   - Examen: {ex.curso}, fecha: {ex.fecha}, avisos: {ex.avisos}")

session.close()
