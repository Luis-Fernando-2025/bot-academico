# fix_avisos.py
from models import SessionLocal, Examen

def fix_avisos():
    session = SessionLocal()
    exámenes = session.query(Examen).all()
    cambios = 0

    for ex in exámenes:
        avisos_lista = [int(x) for x in ex.avisos.split(",") if x.strip().isdigit()]
        avisos_filtrados = sorted([d for d in avisos_lista if d >= 5], reverse=True)

        if avisos_lista != avisos_filtrados:
            ex.avisos = ",".join(str(d) for d in avisos_filtrados)
            cambios += 1
            print(f"[FIX] Examen '{ex.curso}' ({ex.fecha}) -> Avisos: {ex.avisos}")

    session.commit()
    session.close()
    print(f"\n[INFO] Corrección completada. Exámenes actualizados: {cambios}")

if __name__ == "__main__":
    fix_avisos()
