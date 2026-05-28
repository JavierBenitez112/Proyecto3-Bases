from db import Neo4jConnection


def marcar_faltante(pieza_id):
    conn = Neo4jConnection()
    with conn.session() as s:
        res = s.run("""
            MATCH (p:Pieza {id:$id})
            SET p.disponible = false
            RETURN p.numero_etiqueta AS num, p.descripcion_visual AS desc
        """, id=pieza_id).single()
    conn.close()
    if res:
        print(f"Pieza #{res['num']} ({res['desc']}) marcada como FALTANTE.")
    else:
        print(f"No existe la pieza '{pieza_id}'.")


def restaurar_pieza(pieza_id):
    conn = Neo4jConnection()
    with conn.session() as s:
        s.run("MATCH (p:Pieza {id:$id}) SET p.disponible = true", id=pieza_id)
    conn.close()
    print(f"Pieza '{pieza_id}' restaurada como disponible.")


def reset_todas():
    conn = Neo4jConnection()
    with conn.session() as s:
        s.run("MATCH (p:Pieza) SET p.disponible = true")
    conn.close()
    print("Todas las piezas marcadas como disponibles.")
