import argparse
import json
from pathlib import Path
from datetime import datetime
from datetime import datetime as dt

DATA_PATH = Path("data.json")

MIN_DIA = 5
MAX_DIA = 30
MAX_AVISOS = 4
AVISOS_DEFAULT = [30, 10, 5]

# ---------- Utilidades ----------
def load_json(path, default=None):
    if not path.exists():
        if default is not None:
            return default
        raise FileNotFoundError(f"No existe {path.resolve()}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def normalizar_avisos(avisos):
    if avisos is None:
        return AVISOS_DEFAULT
    try:
        avisos = [int(x) for x in avisos]
    except ValueError:
        raise ValueError("Todos los avisos deben ser números enteros.")
    filtrados = sorted({d for d in avisos if MIN_DIA <= d <= MAX_DIA}, reverse=True)
    if not filtrados:
        return AVISOS_DEFAULT
    return filtrados[:MAX_AVISOS]

def find_student(data, nombre):
    for i, st in enumerate(data):
        if st.get("nombre") == nombre:
            return i, st
    return None, None

def find_course(examenes, curso):
    for i, ex in enumerate(examenes):
        if ex.get("curso") == curso:
            return i, ex
    return None, None

def validar_fecha(fecha_str):
    try:
        dt.strptime(fecha_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def print_student_summary(st):
    print(f"\n— {st['nombre']} ({st['telefono']}) —")
    usar_globales = st.get("usar_globales", False)
    print(f"  usar_globales: {usar_globales}")
    if usar_globales:
        print(f"  avisos_globales: {st.get('avisos_globales', [])}")
    print("  Exámenes:")
    for ex in st.get("examenes", []):
        print(f"    • {ex['curso']} ({ex['fecha']}) -> avisos: {ex.get('avisos', [])}")

# ---------- CLI ----------
def build_parser():
    p = argparse.ArgumentParser(
        description="Gestiona estudiantes, cursos y avisos (días antes) en data.json"
    )

    sub = p.add_subparsers(dest="cmd", required=True)

    # Listar
    sub.add_parser("listar", help="Lista todos los estudiantes y sus avisos")

    # Set globales
    s_global = sub.add_parser("set-globales", help="Define avisos_globales de un estudiante")
    s_global.add_argument("--estudiante", required=True, help="Nombre del estudiante")
    s_global.add_argument("--usar-globales", action="store_true",
                          help="Activa usar_globales=True para el estudiante")
    s_global.add_argument("--no-usar-globales", action="store_true",
                          help="Activa usar_globales=False para el estudiante")
    s_global.add_argument("--globales", nargs="+", required=True,
                          help="Lista de días (entre 5 y 30, máx 4). Ej: 30 20 10 5")

    # Set avisos por curso
    s_curso = sub.add_parser("set-curso", help="Define avisos para un curso específico")
    s_curso.add_argument("--estudiante", required=True, help="Nombre del estudiante")
    s_curso.add_argument("--curso", required=True, help="Nombre del curso")
    s_curso.add_argument("--avisos", nargs="+", required=True,
                         help="Lista de días (entre 5 y 30, máx 4). Ej: 20 10 5")

    # Copiar avisos de un curso a todos los cursos del mismo estudiante
    s_copy = sub.add_parser("copiar-a-todos", help="Copia los avisos de un curso a todos los cursos del estudiante")
    s_copy.add_argument("--estudiante", required=True, help="Nombre del estudiante")
    s_copy.add_argument("--curso", required=True, help="Curso fuente cuyos avisos se copiarán")

    # Añadir examen
    s_add = sub.add_parser("add-examen", help="Añade un examen (curso) a un estudiante")
    s_add.add_argument("--estudiante", required=True, help="Nombre del estudiante")
    s_add.add_argument("--curso", required=True, help="Nombre del curso a agregar")
    s_add.add_argument("--fecha", required=True, help="Fecha del examen en formato YYYY-MM-DD")
    s_add.add_argument("--avisos", nargs="*", default=None,
                       help="(Opcional) Lista de días (entre 5 y 30, máx 4). Ej: 30 15 10 5")

    # Cambiar fecha de un examen
    s_upd_date = sub.add_parser("update-fecha", help="Actualiza la fecha de un examen")
    s_upd_date.add_argument("--estudiante", required=True, help="Nombre del estudiante")
    s_upd_date.add_argument("--curso", required=True, help="Curso cuyo examen se actualizará")
    s_upd_date.add_argument("--nueva-fecha", required=True, help="Nueva fecha YYYY-MM-DD")

    # Renombrar curso
    s_rename = sub.add_parser("rename-examen", help="Renombra un curso (examen)")
    s_rename.add_argument("--estudiante", required=True, help="Nombre del estudiante")
    s_rename.add_argument("--curso", required=True, help="Curso actual")
    s_rename.add_argument("--nuevo-curso", required=True, help="Nuevo nombre del curso")

    # Eliminar examen
    s_delete = sub.add_parser("delete-examen", help="Elimina un examen de un estudiante")
    s_delete.add_argument("--estudiante", required=True, help="Nombre del estudiante")
    s_delete.add_argument("--curso", required=True, help="Curso a eliminar")

    return p

# ---------- Comandos ----------
def cmd_listar(data):
    print(f"\n[{datetime.now()}] Listado de estudiantes y configuración actual\n")
    for st in data:
        print_student_summary(st)
    print()

def cmd_set_globales(data, args):
    idx, st = find_student(data, args.estudiante)
    if st is None:
        print(f"❌ Estudiante '{args.estudiante}' no encontrado.")
        return

    avisos = normalizar_avisos(args.globales)
    st["avisos_globales"] = avisos

    if args.usar_globales and args.no_usar_globales:
        print("⚠️ Flags contradictorios: ignoro ambos, se mantiene el valor actual.")
    else:
        if args.usar_globales:
            st["usar_globales"] = True
        if args.no_usar_globales:
            st["usar_globales"] = False

    data[idx] = st
    save_json(DATA_PATH, data)
    print(f"✅ Globales actualizados para {st['nombre']}: {avisos}")
    print_student_summary(st)

def cmd_set_curso(data, args):
    idx, st = find_student(data, args.estudiante)
    if st is None:
        print(f"❌ Estudiante '{args.estudiante}' no encontrado.")
        return

    ex_idx, ex = find_course(st["examenes"], args.curso)
    if ex is None:
        print(f"❌ Curso '{args.curso}' no encontrado para {st['nombre']}.")
        return

    avisos = normalizar_avisos(args.avisos)
    ex["avisos"] = avisos
    st["examenes"][ex_idx] = ex
    data[idx] = st
    save_json(DATA_PATH, data)
    print(f"✅ Avisos del curso '{args.curso}' de {st['nombre']}: {avisos}")
    print_student_summary(st)

def cmd_copiar_a_todos(data, args):
    idx, st = find_student(data, args.estudiante)
    if st is None:
        print(f"❌ Estudiante '{args.estudiante}' no encontrado.")
        return

    ex_idx, ex = find_course(st["examenes"], args.curso)
    if ex is None:
        print(f"❌ Curso '{args.curso}' no encontrado para {st['nombre']}.")
        return

    avisos = normalizar_avisos(ex.get("avisos", []))
    for examen in st["examenes"]:
        examen["avisos"] = avisos

    st["usar_globales"] = False  # Si copia por curso, asumimos configuración por-curso
    data[idx] = st
    save_json(DATA_PATH, data)
    print(f"✅ Avisos del curso '{args.curso}' copiados a TODOS los cursos de {st['nombre']}: {avisos}")
    print_student_summary(st)

def cmd_add_examen(data, args):
    idx, st = find_student(data, args.estudiante)
    if st is None:
        print(f"❌ Estudiante '{args.estudiante}' no encontrado.")
        return

    if not validar_fecha(args.fecha):
        print("❌ Fecha inválida. Usa el formato YYYY-MM-DD.")
        return

    ex_idx, _ = find_course(st["examenes"], args.curso)
    if ex_idx is not None:
        print(f"❌ Ya existe un examen para el curso '{args.curso}' en {st['nombre']}. Usa rename-examen o update-fecha.")
        return

    avisos = normalizar_avisos(args.avisos) if args.avisos else []
    st["examenes"].append({
        "curso": args.curso,
        "fecha": args.fecha,
        "avisos": avisos
    })
    data[idx] = st
    save_json(DATA_PATH, data)
    print(f"✅ Examen añadido para {st['nombre']}: {args.curso} el {args.fecha} (avisos: {avisos if avisos else '(usará globales o default)'})")
    print_student_summary(st)

def cmd_update_fecha(data, args):
    idx, st = find_student(data, args.estudiante)
    if st is None:
        print(f"❌ Estudiante '{args.estudiante}' no encontrado.")
        return

    if not validar_fecha(args.nueva_fecha):
        print("❌ Fecha inválida. Usa el formato YYYY-MM-DD.")
        return

    ex_idx, ex = find_course(st["examenes"], args.curso)
    if ex is None:
        print(f"❌ Curso '{args.curso}' no encontrado para {st['nombre']}.")
        return

    ex["fecha"] = args.nueva_fecha
    st["examenes"][ex_idx] = ex
    data[idx] = st
    save_json(DATA_PATH, data)
    print(f"✅ Fecha actualizada: {st['nombre']} - {args.curso} ahora es {args.nueva_fecha}")
    print_student_summary(st)

def cmd_rename_examen(data, args):
    idx, st = find_student(data, args.estudiante)
    if st is None:
        print(f"❌ Estudiante '{args.estudiante}' no encontrado.")
        return

    ex_idx, ex = find_course(st["examenes"], args.curso)
    if ex is None:
        print(f"❌ Curso '{args.curso}' no encontrado para {st['nombre']}.")
        return

    # comprobar que no exista ya el nuevo nombre
    other_idx, _ = find_course(st["examenes"], args.nuevo-curso) if False else (None, None)  # placeholder
    for cur in st["examenes"]:
        if cur["curso"] == args.nuevo_curso:
            print(f"❌ Ya existe un curso llamado '{args.nuevo_curso}' para {st['nombre']}.")
            return

    ex["curso"] = args.nuevo_curso
    st["examenes"][ex_idx] = ex
    data[idx] = st
    save_json(DATA_PATH, data)
    print(f"✅ Curso renombrado: '{args.curso}' -> '{args.nuevo_curso}' en {st['nombre']}")
    print_student_summary(st)

def cmd_delete_examen(data, args):
    idx, st = find_student(data, args.estudiante)
    if st is None:
        print(f"❌ Estudiante '{args.estudiante}' no encontrado.")
        return

    ex_idx, ex = find_course(st["examenes"], args.curso)
    if ex is None:
        print(f"❌ Curso '{args.curso}' no encontrado para {st['nombre']}.")
        return

    st["examenes"].pop(ex_idx)
    data[idx] = st
    save_json(DATA_PATH, data)
    print(f"✅ Examen eliminado: {args.curso} de {st['nombre']}")
    print_student_summary(st)

def main():
    parser = build_parser()
    args = parser.parse_args()

    try:
        data = load_json(DATA_PATH, [])
    except Exception as e:
        print(f"❌ Error cargando data.json: {e}")
        return

    if args.cmd == "listar":
        cmd_listar(data)
    elif args.cmd == "set-globales":
        cmd_set_globales(data, args)
    elif args.cmd == "set-curso":
        cmd_set_curso(data, args)
    elif args.cmd == "copiar-a-todos":
        cmd_copiar_a_todos(data, args)
    elif args.cmd == "add-examen":
        cmd_add_examen(data, args)
    elif args.cmd == "update-fecha":
        cmd_update_fecha(data, args)
    elif args.cmd == "rename-examen":
        cmd_rename_examen(data, args)
    elif args.cmd == "delete-examen":
        cmd_delete_examen(data, args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
