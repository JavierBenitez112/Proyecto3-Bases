from src.schema import aplicar_schema
from src.loader import cargar_todos
from src.missing import marcar_faltante, restaurar_pieza, reset_todas
from src.solver import (armar_rompecabezas, obtener_puzzles_disponibles,
                        obtener_piezas_por_puzzle, validar_pieza_pertenece_puzzle,
                        obtener_info_puzzle)
from src.db import Neo4jConnection


def menu():
    print("""
╔══════════════════════════════════════════╗
║   ROMPECABEZAS - Base de Datos de Grafos  ║
╠══════════════════════════════════════════╣
║ 1. Verificar conexion                     ║
║ 2. Aplicar schema (constraints)           ║
║ 3. Cargar todos los puzzles               ║
║ 4. Marcar pieza como faltante             ║
║ 5. Restaurar pieza                        ║
║ 6. Reset (todas disponibles)              ║
║ 7. ARMAR rompecabezas (interactivo)       ║
║ 0. Salir                                  ║
╚══════════════════════════════════════════╝
""")


def _armar_rompecabezas_interactivo():
    """Flujo interactivo: puzzle -> pieza inicial -> marcar faltantes -> armar."""

    print("\n" + "="*55)
    print("  SELECCIONAR PUZZLE")
    print("="*55)

    puzzles = obtener_puzzles_disponibles()
    if not puzzles:
        print("No hay puzzles disponibles. Carga algunos primero (opcion 3).")
        return

    for i, p in enumerate(puzzles, 1):
        faltantes_str = f" ({p['piezas_faltantes']} faltante)" if p['piezas_faltantes'] else ""
        print(f"{i}. {p['nombre']} ({p['tipo']}) - {p['total_piezas']} piezas{faltantes_str}")

    try:
        opcion = input("\nElige numero de puzzle: ").strip()
        idx = int(opcion) - 1
        if idx < 0 or idx >= len(puzzles):
            print("Opcion invalida.")
            return
        puzzle_id = puzzles[idx]['id']
    except ValueError:
        print("Opcion invalida.")
        return

    info = obtener_info_puzzle(puzzle_id)
    if not info:
        print(f"No se pudo obtener informacion del puzzle.")
        return

    print("\n" + "="*55)
    print(f"  PUZZLE: {info['nombre']}")
    print("="*55)
    print(f"Tipo: {info['tipo']}")
    print(f"Tema: {info['tema']}")
    print(f"Material: {info['material']}")
    print(f"Total piezas: {info['total_piezas']}")
    if info['piezas_faltantes']:
        print(f"Piezas faltantes: {info['piezas_faltantes']}")
    print(f"Clusters: {info['total_clusters']}")

    piezas_por_cluster = obtener_piezas_por_puzzle(puzzle_id)

    print("\n" + "-"*55)
    print("  PIEZAS POR CLUSTER")
    print("-"*55)
    for cluster in piezas_por_cluster:
        cluster_nombre = cluster['cluster_nombre']
        piezas = cluster['piezas']
        disponibles = len([p for p in piezas if p['disponible']])
        total = len(piezas)
        print(f"\n{cluster_nombre}: {disponibles}/{total} disponibles")
        for p in piezas:
            status = "OK" if p['disponible'] else "FALTANTE"
            if p['fila'] is not None and p['columna'] is not None:
                print(f"  - {p['id']}: {p['descripcion']} ({p['fila']},{p['columna']}) [{status}]")
            else:
                print(f"  - {p['id']}: {p['descripcion']} [{status}]")

    print("\n" + "-"*55)
    print("  SELECCIONAR PIEZA INICIAL")
    print("-"*55)

    pieza_id = input("ID de pieza inicial (ej: ex_1, mo_1, ci_0_0): ").strip()

    if not validar_pieza_pertenece_puzzle(pieza_id, puzzle_id):
        print(f"Error: la pieza '{pieza_id}' no pertenece a '{info['nombre']}'.")
        return

    print(f"\nArmando {info['nombre']} comenzando con pieza {pieza_id}...")

    print("\n" + "-"*55)
    print("  PIEZAS FALTANTES")
    print("-"*55)

    while True:
        print("\nOpciones:")
        print("  1. Ingresar ID de pieza faltante")
        print("  2. No hay piezas faltantes, continuar")

        opcion = input("\nElige opcion (1-2): ").strip()

        if opcion == "1":
            pieza_faltante = input("ID de pieza faltante (ej: ex_5, mo_3, ci_0_1): ").strip()
            if validar_pieza_pertenece_puzzle(pieza_faltante, puzzle_id):
                marcar_faltante(pieza_faltante)
                print(f"Pieza {pieza_faltante} marcada como faltante")
            else:
                print(f"Error: la pieza '{pieza_faltante}' no pertenece a este puzzle.")
        elif opcion == "2":
            break
        else:
            print("Opcion invalida. Elige 1 o 2.")

    armar_rompecabezas(pieza_id)


def main():
    while True:
        menu()
        op = input("Opcion: ").strip()
        if op == "1":
            conn = Neo4jConnection()
            conn.verify()
            conn.close()
        elif op == "2":
            aplicar_schema()
        elif op == "3":
            cargar_todos()
        elif op == "4":
            pid = input("ID de pieza a marcar faltante (ej: ex_3): ").strip()
            marcar_faltante(pid)
        elif op == "5":
            pid = input("ID de pieza a restaurar: ").strip()
            restaurar_pieza(pid)
        elif op == "6":
            reset_todas()
        elif op == "7":
            _armar_rompecabezas_interactivo()
        elif op == "0":
            print("Adios")
            break
        else:
            print("Opcion invalida.")


if __name__ == "__main__":
    main()
