import json
import glob
from src.db import Neo4jConnection


def cargar_puzzle(session, data):
    puzzle_data = data['puzzle']
    session.run("""
        MERGE (p:Puzzle {id:$id})
        SET p.nombre=$nombre, p.tipo=$tipo, p.marca=$marca,
            p.material=$material, p.tema=$tema, p.tiene_bandeja=$tiene_bandeja
    """, id=puzzle_data['id'], nombre=puzzle_data['nombre'],
        tipo=puzzle_data['tipo'], marca=puzzle_data['marca'],
        material=puzzle_data['material'], tema=puzzle_data['tema'],
        tiene_bandeja=puzzle_data['tiene_bandeja'])

    for cluster in data['clusters']:
        session.run("""
            MERGE (c:Cluster {id:$id})
            SET c.nombre_cluster=$nombre_cluster,
                c.total_piezas=$total_piezas
            WITH c
            MATCH (p:Puzzle {id:$puzzle_id})
            MERGE (c)-[:PERTENECE_A]->(p)
        """, id=cluster['id'], puzzle_id=cluster['puzzle_id'],
             nombre_cluster=cluster['nombre_cluster'],
             total_piezas=cluster['total_piezas'])

        for pieza in cluster['piezas']:
            session.run("""
                MERGE (pz:Pieza {id:$id})
                SET pz.numero_etiqueta=$numero_etiqueta,
                    pz.descripcion_visual=$descripcion_visual,
                    pz.disponible=$disponible,
                    pz.fila=$fila, pz.columna=$columna
                WITH pz
                MATCH (c:Cluster {id:$cluster_id})
                MERGE (pz)-[:PERTENECE_A]->(c)
            """, **pieza)

    for conn in data.get('conexiones', []):
        if not isinstance(conn, dict):
            continue
        session.run("""
            MATCH (a:Pieza {id:$origen}), (b:Pieza {id:$destino})
            MERGE (a)-[r1:CONECTA_CON]->(b)
            SET r1.descripcion_desde = $desc_desde,
                r1.descripcion_hacia = $desc_hacia,
                r1.tipo_ensamble = $tipo
            MERGE (b)-[r2:CONECTA_CON]->(a)
            SET r2.descripcion_desde = $desc_hacia,
                r2.descripcion_hacia = $desc_desde,
                r2.tipo_ensamble = $tipo
        """, origen=conn['origen'], destino=conn['destino'],
             desc_desde=conn['desc_desde'], desc_hacia=conn['desc_hacia'],
             tipo=conn['tipo'])


def cargar_todos():
    conn = Neo4jConnection()
    with conn.session() as s:
        for archivo in glob.glob("data/puzzles/*.json"):
            with open(archivo, encoding="utf-8") as f:
                data = json.load(f)
            cargar_puzzle(s, data)
            print(f"Cargado: {data['puzzle']['nombre']}")
    conn.close()


if __name__ == "__main__":
    cargar_todos()
