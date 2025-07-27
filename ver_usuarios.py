# ver_usuarios.py
from models import SessionLocal, Usuario, Examen, init_db

def main():
    init_db()
    session = SessionLocal()
    print("\n=== LISTADO DE USUARIOS Y EXÁMENES ===")

    usuarios = session.query(Usuario).all()
    if not usuarios:
        print("No hay usuarios registrados.")
    else:
        for u in usuarios:
            print(f"\nUsuario: {u.telefono} | Zona horaria: {u.timezone}")
            print(f"   Avisos globales: {u.avisos_globales} | Usar globales: {u.usar_globales}")
            for ex in u.examenes:
                print(f"      - Examen: {ex.curso} | Fecha: {ex.fecha} | Avisos: {ex.avisos or 'Por defecto'}")

    session.close()

if __name__ == "__main__":
    main()
