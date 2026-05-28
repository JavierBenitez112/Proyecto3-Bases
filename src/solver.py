from collections import deque
from src.db import Neo4jConnection

# NOTA SOBRE EL MODELO:
# Los campos Puzzle.tipo, Puzzle.marca, Puzzle.material, Puzzle.tema son DESCRIPTIVOS
# (metadatos). El algoritmo BFS no los consulta para decidir qué hacer.
# Esto es una fortaleza del diseño: un único BFS resuelve puzzles LIBRE, BANDEJA y GRID
# sin ramificación. Los campos sirven para: documentación, filtros de consulta y validación.


def _nombre_pieza(p):
    """Nombre legible para la pieza, tenga o no número.

    Prioridad: numero etiqueta -> coordenadas (fila,columna) -> descripcion
    """
    if p.get('numero') is not None:
        return f"#{p['numero']}"
    if p.get('fila') is not None and p.get('columna') is not None:
        return f"({p['fila']},{p['columna']})"
    return f"'{p['descripcion']}'"


def _obtener_pieza(session, pieza_id):
    return session.run("""
        MATCH (p:Pieza {id:$id})
        RETURN p.id AS id, p.numero_etiqueta AS numero,
               p.descripcion_visual AS descripcion,
               p.disponible AS disponible, p.fila AS fila,
               p.columna AS columna
    """, id=pieza_id).single()


def _obtener_vecinos(session, pieza_id):
    return session.run("""
        MATCH (p:Pieza {id:$id})-[r:CONECTA_CON]->(v:Pieza)
        RETURN v.id AS id, v.numero_etiqueta AS numero,
               v.descripcion_visual AS descripcion, v.disponible AS disponible,
               r.descripcion_desde AS desde, r.descripcion_hacia AS hacia,
               r.tipo_ensamble AS tipo
    """, id=pieza_id).data()


def obtener_puzzles_disponibles():
    """Retorna lista de puzzles con metadatos."""
    conn = Neo4jConnection()
    try:
        with conn.session() as s:
            resultado = s.run("""
                MATCH (p:Puzzle)<-[:PERTENECE_A]-(c:Cluster)<-[:PERTENECE_A]-(pz:Pieza)
                RETURN DISTINCT
                  p.id AS id, p.nombre AS nombre, p.tipo AS tipo,
                  p.material AS material, p.tema AS tema,
                  COUNT(DISTINCT pz) AS total_piezas,
                  SUM(CASE WHEN pz.disponible = false THEN 1 ELSE 0 END) AS piezas_faltantes
                ORDER BY p.nombre
            """).data()
            return resultado
    finally:
        conn.close()


def obtener_piezas_por_puzzle(puzzle_id):
    """Retorna piezas de un puzzle agrupadas por cluster."""
    conn = Neo4jConnection()
    try:
        with conn.session() as s:
            resultado = s.run("""
                MATCH (pz:Pieza)-[:PERTENECE_A]->(c:Cluster)-[:PERTENECE_A]->(p:Puzzle {id:$puzzle_id})
                RETURN c.id AS cluster_id, c.nombre_cluster AS cluster_nombre,
                       COLLECT({
                           id: pz.id,
                           numero: pz.numero_etiqueta,
                           descripcion: pz.descripcion_visual,
                           disponible: pz.disponible,
                           fila: pz.fila,
                           columna: pz.columna
                       }) AS piezas
                ORDER BY c.id
            """, puzzle_id=puzzle_id).data()
            return resultado
    finally:
        conn.close()


def validar_pieza_pertenece_puzzle(pieza_id, puzzle_id):
    """Valida que una pieza pertenezca a un puzzle."""
    conn = Neo4jConnection()
    try:
        with conn.session() as s:
            resultado = s.run("""
                MATCH (pz:Pieza {id:$pieza_id})-[:PERTENECE_A]->(c:Cluster)-[:PERTENECE_A]->(p:Puzzle {id:$puzzle_id})
                RETURN count(pz) > 0 AS existe
            """, pieza_id=pieza_id, puzzle_id=puzzle_id).single()
            return resultado['existe'] if resultado else False
    finally:
        conn.close()


def obtener_info_puzzle(puzzle_id):
    """Obtiene metadatos completos de un puzzle."""
    conn = Neo4jConnection()
    try:
        with conn.session() as s:
            resultado = s.run("""
                MATCH (p:Puzzle {id:$puzzle_id})<-[:PERTENECE_A]-(c:Cluster)<-[:PERTENECE_A]-(pz:Pieza)
                RETURN p.id AS id, p.nombre AS nombre, p.tipo AS tipo,
                       p.material AS material, p.tema AS tema,
                       p.tiene_bandeja AS tiene_bandeja,
                       COUNT(DISTINCT c) AS total_clusters,
                       COUNT(DISTINCT pz) AS total_piezas,
                       SUM(CASE WHEN pz.disponible = false THEN 1 ELSE 0 END) AS piezas_faltantes
            """, puzzle_id=puzzle_id).single()
            return resultado if resultado else None
    finally:
        conn.close()


def listar_clusters(puzzle_id):
    """Lista los clusters de un puzzle para elegir piezas iniciales.

    Nota: El BFS solo arma el cluster de la pieza inicial, así que para
    puzzles multi-cluster hay que ejecutar el algoritmo una vez por cluster.
    """
    conn = Neo4jConnection()
    try:
        with conn.session() as s:
            rows = s.run("""
                MATCH (c:Cluster)-[:PERTENECE_A]->(p:Puzzle {id:$pid})
                OPTIONAL MATCH (c)<-[:PERTENECE_A]-(pz:Pieza)
                RETURN c.id AS cluster, c.nombre_cluster AS nombre,
                       count(pz) AS piezas
                ORDER BY c.id
            """, pid=puzzle_id).data()
            return rows
    finally:
        conn.close()


def armar_rompecabezas(pieza_inicial_id):
    conn = Neo4jConnection()
    pasos, advertencias, visitados = [], [], set()
    cola = deque()

    with conn.session() as s:
        inicial = _obtener_pieza(s, pieza_inicial_id)
        if not inicial:
            print(f"La pieza '{pieza_inicial_id}' no existe.")
            conn.close()
            return

        cola.append((pieza_inicial_id, None, None, None))
        print("\n" + "="*55)
        print("  GUIA PARA ARMAR EL ROMPECABEZAS")
        print("="*55)

        paso = 1
        while cola:
            pid, ancla_origen, desde, hacia = cola.popleft()
            if pid in visitados:
                continue
            visitados.add(pid)
            pieza = _obtener_pieza(s, pid)

            if not pieza['disponible']:
                nombre_pieza = _nombre_pieza(pieza)
                adv = (f"Paso {paso}: Pieza {nombre_pieza} "
                       f"({pieza['descripcion']}) -- FALTANTE")
                advertencias.append(adv)
                print(f"\n[ADVERTENCIA] La pieza {nombre_pieza} "
                      f"({pieza['descripcion']}) esta FALTANTE. "
                      f"Se continua con el resto del armado.")
                if ancla_origen:
                    print(f"\n  Paso {paso}: [FALTANTE] Aqui iria la pieza "
                          f"{nombre_pieza} -- {pieza['descripcion']}")
                    print(f"           -> Deberia encajar en: {hacia} "
                          f"de la pieza {ancla_origen}")
                else:
                    print(f"\n  Paso {paso}: [FALTANTE] La pieza inicial "
                          f"{nombre_pieza} no esta disponible.")
            else:
                nombre_pieza = _nombre_pieza(pieza)
                if ancla_origen is None:
                    print(f"\n  Paso {paso}: [INICIO] Toma la pieza {nombre_pieza}")
                    print(f"             ({pieza['descripcion']}) -- colócala como base.")
                else:
                    print(f"\n  Paso {paso}: [PIEZA] Toma la pieza {nombre_pieza}")
                    print(f"             ({pieza['descripcion']})")
                    print(f"             -> Tomala por: {desde}")
                    print(f"             -> Encájala en: {hacia} de la pieza {ancla_origen}")

            paso += 1

            # Construir etiqueta de ancla con marca de FALTANTE si aplica
            ancla = _nombre_pieza(pieza)
            if not pieza['disponible']:
                ancla += " (FALTANTE)"

            for v in _obtener_vecinos(s, pid):
                if v['id'] not in visitados:
                    cola.append((v['id'], ancla, v['desde'], v['hacia']))

        print("\n" + "="*55)
        if advertencias:
            print(f"\n  [RESUMEN] {len(advertencias)} pieza(s) faltante(s):")
            for a in advertencias:
                print(f"     * {a}")
            print("\n  El rompecabezas se armo PARCIALMENTE.")
        else:
            print("  Rompecabezas completo! Todas las piezas estaban disponibles.")
        print("="*55 + "\n")

    conn.close()
