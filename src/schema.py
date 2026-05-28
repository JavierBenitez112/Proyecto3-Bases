from db import Neo4jConnection

CONSTRAINTS = [
    "CREATE CONSTRAINT puzzle_id IF NOT EXISTS FOR (p:Puzzle) REQUIRE p.id IS UNIQUE",
    "CREATE CONSTRAINT cluster_id IF NOT EXISTS FOR (c:Cluster) REQUIRE c.id IS UNIQUE",
    "CREATE CONSTRAINT pieza_id IF NOT EXISTS FOR (p:Pieza) REQUIRE p.id IS UNIQUE",
]


def aplicar_schema():
    conn = Neo4jConnection()
    with conn.session() as s:
        for c in CONSTRAINTS:
            s.run(c)
    conn.close()
    print("Constraints aplicados.")


if __name__ == "__main__":
    aplicar_schema()
