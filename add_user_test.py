# add_user_test.py
def pedir_avisos(usuario_avisos="30,20,10,5"):
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

def main():
    print("=== PRUEBA DE VALIDACIÓN DE AVISOS ===")
    avisos_final = pedir_avisos()
    print(f"✅ Avisos seleccionados: {avisos_final}")

if __name__ == "__main__":
    main()
