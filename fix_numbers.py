# fix_numbers.py
from models import SessionLocal, Usuario

def fix_numbers():
    session = SessionLocal()
    usuarios = session.query(Usuario).all()
    cambios = 0

    for u in usuarios:
        if not u.telefono.startswith("whatsapp:"):
            old_number = u.telefono
            u.telefono = f"whatsapp:{u.telefono}"
            cambios += 1
            print(f"[FIX] {old_number} -> {u.telefono}")

    session.commit()
    session.close()
    print(f"Corrección completada. Números modificados: {cambios}")

if __name__ == "__main__":
    fix_numbers()
