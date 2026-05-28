import json
import os


def generar_grid(puzzle_id, nombre, tema, filas, columnas,
                 marca="Desconocida", material="Carton",
                 tiene_bandeja=True, prefijo="g"):
    """Genera el JSON de un puzzle tipo cuadricula filas x columnas."""
    cluster_id = f"cluster_{puzzle_id}_1"
    piezas = []
    for f in range(filas):
        for c in range(columnas):
            piezas.append({
                "id": f"{prefijo}_{f}_{c}",
                "cluster_id": cluster_id,
                "numero_etiqueta": None,
                "descripcion_visual": f"Pieza en posicion ({f},{c})",
                "disponible": True,
                "fila": f,
                "columna": c
            })

    conexiones = []
    for f in range(filas):
        for c in range(columnas):
            origen = f"{prefijo}_{f}_{c}"
            if c + 1 < columnas:
                conexiones.append({
                    "origen": origen,
                    "destino": f"{prefijo}_{f}_{c+1}",
                    "desc_desde": "lado derecho",
                    "desc_hacia": "lado izquierdo",
                    "tipo": "ENCAJE"
                })
            if f + 1 < filas:
                conexiones.append({
                    "origen": origen,
                    "destino": f"{prefijo}_{f+1}_{c}",
                    "desc_desde": "lado inferior",
                    "desc_hacia": "lado superior",
                    "tipo": "ENCAJE"
                })

    data = {
        "puzzle": {
            "id": puzzle_id,
            "nombre": nombre,
            "tipo": "GRID",
            "marca": marca,
            "material": material,
            "tema": tema,
            "tiene_bandeja": tiene_bandeja
        },
        "clusters": [
            {
                "id": cluster_id,
                "puzzle_id": puzzle_id,
                "nombre_cluster": "Escena completa",
                "total_piezas": filas * columnas,
                "piezas": piezas
            }
        ],
        "conexiones": conexiones
    }

    os.makedirs("data/puzzles", exist_ok=True)
    ruta = f"data/puzzles/{puzzle_id}.json"
    with open(ruta, "w", encoding="utf-8") as fp:
        json.dump(data, fp, ensure_ascii=False, indent=2)
    print(f"Generado {ruta} -- {filas}x{columnas} = {filas*columnas} piezas")


if __name__ == "__main__":
    generar_grid(
        puzzle_id="puzzle_city",
        nombre="City Airplane Scene",
        tema="Ciudad con avion",
        filas=4,
        columnas=6,
        material="Carton",
        prefijo="ci"
    )

    generar_grid(
        puzzle_id="puzzle_bears",
        nombre="Animals Scene",
        tema="Animales de bosque",
        filas=5,
        columnas=6,
        material="Carton",
        prefijo="be"
    )
