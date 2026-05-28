# Proyecto 03 — Elección de Tecnologías de Base de Datos
## Plan de Implementación para Claude Code

**Curso:** CC3089 Base de Datos 2 — UVG, Semestre I 2026
**Tema:** Modelado y resolución de rompecabezas mediante base de datos de grafos
**Tecnología elegida:** Neo4j Aura (cloud)

---

## 0. Resumen ejecutivo (contexto para Claude Code)

Estamos resolviendo un problema de armado de rompecabezas físicos no convencionales. Las piezas están **numeradas** y se conectan entre sí de forma irregular (no en cuadrícula fija, salvo un caso). El sistema debe:

1. Modelar piezas, rompecabezas y sus relaciones en una base de datos de grafos.
2. Soportar **múltiples clusters** (un mismo set físico puede contener varios sub-rompecabezas independientes).
3. Soportar **piezas faltantes**: el usuario indica qué pieza no tiene, y el algoritmo continúa normalmente emitiendo una advertencia.
4. Recibir una **pieza inicial cualquiera** del usuario y generar la guía paso a paso de cómo armar el rompecabezas.

### ¿Por qué Neo4j (base de datos de grafos) y no SQL?

| Criterio | Neo4j (elegida) | PostgreSQL / SQL |
|---|---|---|
| Modelado de conexiones pieza-a-pieza | Natural (aristas) | Tabla de adyacencia + JOINs |
| Recorrido desde pieza inicial (BFS/DFS) | Cypher nativo, O(1) por relación | CTE recursivos, más complejos |
| Clusters (sub-rompecabezas) | Componentes desconectados nativos | Requiere lógica adicional |
| Piezas faltantes | Atributo de nodo, no afecta estructura | Igual de simple, pero traversal más caro |
| Escalabilidad (agregar puzzles) | Trivial | Trivial pero consultas más lentas |

El núcleo del problema **es un grafo**. La elección de Neo4j reduce la complejidad de la solución, que es justo el criterio que la rúbrica premia ("la elección de tecnología impactará en la dificultad de la solución").

---

## 1. Stack tecnológico

- **Base de datos:** Neo4j Aura Free (cloud, sin instalación local)
- **Lenguaje:** Python 3.10+
- **Driver:** `neo4j` (driver oficial)
- **Gestión de entorno:** `python-dotenv` para credenciales
- **CLI:** entrada/salida por consola (suficiente para la demo)
- **Visualización:** Neo4j Aura Browser (incluido, muestra el grafo visualmente)

Dependencias (`requirements.txt`):
```
neo4j>=5.0
python-dotenv>=1.0
```

---

## 2. Configuración de Neo4j Aura (paso a paso, manual)

> Esto lo hace el usuario una sola vez. Claude Code no puede crear la instancia, solo consumirla.

1. Ir a https://neo4j.com/product/auradb/ y crear cuenta gratuita.
2. Crear una instancia **AuraDB Free**.
3. Al crearla, Aura muestra **una sola vez** las credenciales:
   - `NEO4J_URI` (formato `neo4j+s://xxxxx.databases.neo4j.io`)
   - `NEO4J_USERNAME` (normalmente `neo4j`)
   - `NEO4J_PASSWORD`
4. Descargar el archivo de credenciales o copiarlas a un `.env` (ver sección 4).
5. Esperar a que la instancia tenga estado **Running**.

---

## 3. Estructura del proyecto

```
rompecabezas-bd2/
├── .env                      # credenciales Aura (NO subir a git)
├── .env.example              # plantilla de credenciales
├── requirements.txt
├── README.md
├── data/
│   └── puzzles/
│       ├── excavator.json
│       ├── monsters.json
│       ├── dolphins.json
│       └── city_grid.json
├── src/
│   ├── __init__.py
│   ├── db.py                 # conexión a Neo4j
│   ├── schema.py             # constraints/índices
│   ├── loader.py             # carga puzzles desde JSON
│   ├── missing.py            # marcar/restaurar piezas faltantes
│   ├── solver.py             # algoritmo BFS de armado
│   └── main.py               # CLI principal
└── tests/
    └── test_solver.py        # pruebas del algoritmo
```

---

## 4. Archivos de configuración

### `.env.example`
```
NEO4J_URI=neo4j+s://XXXXXXXX.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=tu_password_aqui
```

### `.gitignore`
```
.env
__pycache__/
*.pyc
venv/
```

---

## 5. Modelo de datos (esquema del grafo)

### Nodos

**`Puzzle`** — un set físico de rompecabezas
| Propiedad | Tipo | Descripción |
|---|---|---|
| `id` | string | identificador único |
| `nombre` | string | nombre del puzzle |
| `tipo` | string | `LIBRE` \| `GRID` \| `BANDEJA` |
| `marca` | string | marca comercial |
| `material` | string | madera, foam, cartón |
| `tema` | string | temática de la imagen |
| `tiene_bandeja` | bool | si requiere marco/base |

**`Cluster`** — un sub-rompecabezas independiente dentro de un Puzzle
| Propiedad | Tipo | Descripción |
|---|---|---|
| `id` | string | identificador único |
| `puzzle_id` | string | a qué Puzzle pertenece |
| `nombre_cluster` | string | nombre descriptivo |
| `total_piezas` | int | número de piezas |

**`Pieza`** — un nodo del grafo
| Propiedad | Tipo | Descripción |
|---|---|---|
| `id` | string | identificador único |
| `cluster_id` | string | a qué Cluster pertenece |
| `numero_etiqueta` | int/null | número escrito físicamente |
| `descripcion_visual` | string | descripción para guiar al usuario |
| `fila` | int/null | solo para puzzles GRID |
| `columna` | int/null | solo para puzzles GRID |
| `disponible` | bool | `false` si la pieza está faltante |

### Relaciones

**`(:Cluster)-[:PERTENECE_A]->(:Puzzle)`**
**`(:Pieza)-[:PERTENECE_A]->(:Cluster)`**
**`(:Pieza)-[:CONECTA_CON]->(:Pieza)`** con propiedades:
| Propiedad | Descripción |
|---|---|
| `descripcion_desde` | dónde está el conector en la pieza origen |
| `descripcion_hacia` | dónde encaja en la pieza destino |
| `tipo_ensamble` | `ENCAJE` \| `RANURA` \| `SOLAPE` |

> **Nota de diseño:** las conexiones se modelan dirigidas en Neo4j pero se tratan como bidireccionales en el algoritmo (al cargar, se crea la arista en ambos sentidos, o el BFS consulta sin dirección). Ver `solver.py`.

---

## 6. Implementación de los módulos

### 6.1 `src/db.py` — conexión

```python
import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

class Neo4jConnection:
    def __init__(self):
        uri = os.getenv("NEO4J_URI")
        user = os.getenv("NEO4J_USERNAME")
        password = os.getenv("NEO4J_PASSWORD")
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def session(self):
        return self.driver.session()

    def verify(self):
        with self.session() as s:
            s.run("RETURN 1")
        print("✅ Conexión a Neo4j Aura exitosa.")
```

### 6.2 `src/schema.py` — constraints

```python
from src.db import Neo4jConnection

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
    print("✅ Constraints aplicados.")

if __name__ == "__main__":
    aplicar_schema()
```

### 6.3 `src/loader.py` — carga desde JSON

```python
import json, glob
from src.db import Neo4jConnection

def cargar_puzzle(session, data):
    # 1. Puzzle
    session.run("""
        MERGE (p:Puzzle {id:$id})
        SET p.nombre=$nombre, p.tipo=$tipo, p.marca=$marca,
            p.material=$material, p.tema=$tema, p.tiene_bandeja=$tiene_bandeja
    """, **data['puzzle'])

    # 2. Clusters + Piezas
    for cluster in data['clusters']:
        session.run("""
            MERGE (c:Cluster {id:$id})
            SET c.puzzle_id=$puzzle_id, c.nombre_cluster=$nombre_cluster,
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
                SET pz.cluster_id=$cluster_id,
                    pz.numero_etiqueta=$numero_etiqueta,
                    pz.descripcion_visual=$descripcion_visual,
                    pz.disponible=$disponible,
                    pz.fila=$fila, pz.columna=$columna
                WITH pz
                MATCH (c:Cluster {id:$cluster_id})
                MERGE (pz)-[:PERTENECE_A]->(c)
            """, **pieza)

    # 3. Conexiones (bidireccionales)
    for conn in data['conexiones']:
        session.run("""
            MATCH (a:Pieza {id:$origen}), (b:Pieza {id:$destino})
            MERGE (a)-[:CONECTA_CON {
                descripcion_desde:$desc_desde,
                descripcion_hacia:$desc_hacia,
                tipo_ensamble:$tipo
            }]->(b)
            MERGE (b)-[:CONECTA_CON {
                descripcion_desde:$desc_hacia,
                descripcion_hacia:$desc_desde,
                tipo_ensamble:$tipo
            }]->(a)
        """, **conn)

def cargar_todos():
    conn = Neo4jConnection()
    with conn.session() as s:
        for archivo in glob.glob("data/puzzles/*.json"):
            with open(archivo, encoding="utf-8") as f:
                data = json.load(f)
            cargar_puzzle(s, data)
            print(f"✅ Cargado: {data['puzzle']['nombre']}")
    conn.close()

if __name__ == "__main__":
    cargar_todos()
```

### 6.4 `src/missing.py` — gestión de piezas faltantes

```python
from src.db import Neo4jConnection

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
        print(f"⚠️  Pieza #{res['num']} ({res['desc']}) marcada como FALTANTE.")
    else:
        print(f"❌ No existe la pieza '{pieza_id}'.")

def restaurar_pieza(pieza_id):
    conn = Neo4jConnection()
    with conn.session() as s:
        s.run("MATCH (p:Pieza {id:$id}) SET p.disponible = true", id=pieza_id)
    conn.close()
    print(f"✅ Pieza '{pieza_id}' restaurada como disponible.")

def reset_todas():
    conn = Neo4jConnection()
    with conn.session() as s:
        s.run("MATCH (p:Pieza) SET p.disponible = true")
    conn.close()
    print("✅ Todas las piezas marcadas como disponibles.")
```

### 6.5 `src/solver.py` — algoritmo BFS de armado

> **Lógica clave de piezas faltantes:** el grafo NO se modifica. La pieza faltante sigue siendo un nodo con sus conexiones. El BFS la visita, emite una advertencia, registra el paso como `[FALTANTE]` y **continúa encolando sus vecinos normalmente**. Así, si falta una pieza intermedia, el algoritmo igual alcanza las piezas posteriores.

```python
from collections import deque
from src.db import Neo4jConnection

def _obtener_pieza(session, pieza_id):
    return session.run("""
        MATCH (p:Pieza {id:$id})
        RETURN p.id AS id, p.numero_etiqueta AS numero,
               p.descripcion_visual AS descripcion,
               p.disponible AS disponible, p.cluster_id AS cluster_id
    """, id=pieza_id).single()

def _obtener_vecinos(session, pieza_id):
    return session.run("""
        MATCH (p:Pieza {id:$id})-[r:CONECTA_CON]->(v:Pieza)
        RETURN v.id AS id, v.numero_etiqueta AS numero,
               v.descripcion_visual AS descripcion, v.disponible AS disponible,
               r.descripcion_desde AS desde, r.descripcion_hacia AS hacia,
               r.tipo_ensamble AS tipo
    """, id=pieza_id).data()

def armar_rompecabezas(pieza_inicial_id):
    conn = Neo4jConnection()
    pasos, advertencias, visitados = [], [], set()
    cola = deque()

    with conn.session() as s:
        inicial = _obtener_pieza(s, pieza_inicial_id)
        if not inicial:
            print(f"❌ La pieza '{pieza_inicial_id}' no existe.")
            conn.close()
            return

        cola.append((pieza_inicial_id, None, None, None))
        print("\n" + "═"*55)
        print("  GUÍA PARA ARMAR EL ROMPECABEZAS")
        print("═"*55)

        paso = 1
        while cola:
            pid, origen_num, desde, hacia = cola.popleft()
            if pid in visitados:
                continue
            visitados.add(pid)
            pieza = _obtener_pieza(s, pid)

            if not pieza['disponible']:
                adv = (f"Paso {paso}: Pieza #{pieza['numero']} "
                       f"({pieza['descripcion']}) — FALTANTE")
                advertencias.append(adv)
                print(f"\n⚠️  ADVERTENCIA — La pieza #{pieza['numero']} "
                      f"({pieza['descripcion']}) está FALTANTE. "
                      f"Se continúa con el resto del armado.")
                if origen_num:
                    print(f"\n  Paso {paso}: [FALTANTE] Aquí iría la pieza "
                          f"#{pieza['numero']} — {pieza['descripcion']}")
                    print(f"           → Debería encajar en: {hacia} "
                          f"de la pieza #{origen_num}")
                else:
                    print(f"\n  Paso {paso}: [FALTANTE] La pieza inicial "
                          f"#{pieza['numero']} no está disponible.")
            else:
                if origen_num is None:
                    print(f"\n  Paso {paso}: 🟢 INICIO — Toma la pieza "
                          f"#{pieza['numero']}")
                    print(f"             ({pieza['descripcion']}) — colócala como base.")
                else:
                    print(f"\n  Paso {paso}: 🟢 Toma la pieza #{pieza['numero']}")
                    print(f"             ({pieza['descripcion']})")
                    print(f"             → Tómala por: {desde}")
                    print(f"             → Encájala en: {hacia} de la pieza #{origen_num}")

            paso += 1

            # Encolar vecinos SIEMPRE (haya o no advertencia)
            for v in _obtener_vecinos(s, pid):
                if v['id'] not in visitados:
                    cola.append((v['id'], pieza['numero'], v['desde'], v['hacia']))

        print("\n" + "═"*55)
        if advertencias:
            print(f"\n  ⚠️  RESUMEN — {len(advertencias)} pieza(s) faltante(s):")
            for a in advertencias:
                print(f"     • {a}")
            print("\n  El rompecabezas se armó PARCIALMENTE.")
        else:
            print("  ✅ ¡Rompecabezas completo! Todas las piezas estaban disponibles.")
        print("═"*55 + "\n")

    conn.close()
```

### 6.6 `src/main.py` — CLI principal

```python
from src.schema import aplicar_schema
from src.loader import cargar_todos
from src.missing import marcar_faltante, restaurar_pieza, reset_todas
from src.solver import armar_rompecabezas
from src.db import Neo4jConnection

def menu():
    print("""
╔══════════════════════════════════════════╗
║   ROMPECABEZAS — Base de Datos de Grafos  ║
╠══════════════════════════════════════════╣
║ 1. Verificar conexión                     ║
║ 2. Aplicar schema (constraints)           ║
║ 3. Cargar todos los puzzles               ║
║ 4. Marcar pieza como faltante             ║
║ 5. Restaurar pieza                        ║
║ 6. Reset (todas disponibles)              ║
║ 7. ARMAR rompecabezas (pieza inicial)     ║
║ 0. Salir                                  ║
╚══════════════════════════════════════════╝
""")

def main():
    while True:
        menu()
        op = input("Opción: ").strip()
        if op == "1":
            Neo4jConnection().verify()
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
            pid = input("¿Qué pieza tienes? ID inicial (ej: ex_1): ").strip()
            armar_rompecabezas(pid)
        elif op == "0":
            print("Adiós 👋")
            break
        else:
            print("Opción inválida.")

if __name__ == "__main__":
    main()
```

---

## 7. Datos de los rompecabezas (archivos JSON)

> Estos son los puzzles ya modelados a partir de las fotos. Los puzzles `dolphins` y `city_grid` tienen las conexiones marcadas como TODO porque requieren confirmar la disposición exacta de piezas (especialmente delfines por su solapamiento y el grid por sus coordenadas reales).

### `data/puzzles/excavator.json`
```json
{
  "puzzle": {
    "id": "puzzle_excavator", "nombre": "Excavator", "tipo": "LIBRE",
    "marca": "Desconocida", "material": "Madera/Foam",
    "tema": "Vehiculos de construccion", "tiene_bandeja": false
  },
  "clusters": [{
    "id": "cluster_excavator_1", "puzzle_id": "puzzle_excavator",
    "nombre_cluster": "Excavadora completa", "total_piezas": 10,
    "piezas": [
      {"id":"ex_1","cluster_id":"cluster_excavator_1","numero_etiqueta":1,"descripcion_visual":"Pala/cuchara turquesa","disponible":true,"fila":null,"columna":null},
      {"id":"ex_2","cluster_id":"cluster_excavator_1","numero_etiqueta":2,"descripcion_visual":"Brazo superior naranja con rueda negra","disponible":true,"fila":null,"columna":null},
      {"id":"ex_3","cluster_id":"cluster_excavator_1","numero_etiqueta":3,"descripcion_visual":"Articulacion del brazo naranja","disponible":true,"fila":null,"columna":null},
      {"id":"ex_4","cluster_id":"cluster_excavator_1","numero_etiqueta":4,"descripcion_visual":"Cabina izquierda amarilla con tigre","disponible":true,"fila":null,"columna":null},
      {"id":"ex_5","cluster_id":"cluster_excavator_1","numero_etiqueta":5,"descripcion_visual":"Cabina derecha amarilla con ventana","disponible":true,"fila":null,"columna":null},
      {"id":"ex_6","cluster_id":"cluster_excavator_1","numero_etiqueta":6,"descripcion_visual":"Cuerpo inferior izquierdo rojo con texto EXCAVATOR","disponible":true,"fila":null,"columna":null},
      {"id":"ex_7","cluster_id":"cluster_excavator_1","numero_etiqueta":7,"descripcion_visual":"Cuerpo inferior derecho rojo con estrellas","disponible":true,"fila":null,"columna":null},
      {"id":"ex_8","cluster_id":"cluster_excavator_1","numero_etiqueta":8,"descripcion_visual":"Panel lateral derecho naranja/motor","disponible":true,"fila":null,"columna":null},
      {"id":"ex_9","cluster_id":"cluster_excavator_1","numero_etiqueta":9,"descripcion_visual":"Oruga izquierda inferior","disponible":true,"fila":null,"columna":null},
      {"id":"ex_10","cluster_id":"cluster_excavator_1","numero_etiqueta":10,"descripcion_visual":"Oruga derecha inferior","disponible":true,"fila":null,"columna":null}
    ]
  }],
  "conexiones": [
    {"origen":"ex_1","destino":"ex_2","desc_desde":"extremo superior de la pala","desc_hacia":"extremo inferior del brazo","tipo":"ENCAJE"},
    {"origen":"ex_2","destino":"ex_3","desc_desde":"lado inferior del brazo","desc_hacia":"extremo superior de la articulacion","tipo":"ENCAJE"},
    {"origen":"ex_3","destino":"ex_4","desc_desde":"extremo derecho de la articulacion","desc_hacia":"lado izquierdo de la cabina","tipo":"ENCAJE"},
    {"origen":"ex_4","destino":"ex_5","desc_desde":"lado derecho de la cabina izquierda","desc_hacia":"lado izquierdo de la cabina derecha","tipo":"ENCAJE"},
    {"origen":"ex_5","destino":"ex_8","desc_desde":"lado derecho de la cabina derecha","desc_hacia":"parte superior del panel lateral","tipo":"ENCAJE"},
    {"origen":"ex_4","destino":"ex_6","desc_desde":"parte inferior de la cabina izquierda","desc_hacia":"parte superior del cuerpo izquierdo","tipo":"ENCAJE"},
    {"origen":"ex_6","destino":"ex_7","desc_desde":"lado derecho del cuerpo izquierdo","desc_hacia":"lado izquierdo del cuerpo derecho","tipo":"ENCAJE"},
    {"origen":"ex_7","destino":"ex_8","desc_desde":"parte superior del cuerpo derecho","desc_hacia":"parte inferior del panel lateral","tipo":"ENCAJE"},
    {"origen":"ex_6","destino":"ex_9","desc_desde":"parte inferior izquierda del cuerpo","desc_hacia":"parte superior de la oruga izquierda","tipo":"ENCAJE"},
    {"origen":"ex_7","destino":"ex_10","desc_desde":"parte inferior derecha del cuerpo","desc_hacia":"parte superior de la oruga derecha","tipo":"ENCAJE"},
    {"origen":"ex_9","destino":"ex_10","desc_desde":"lado derecho de la oruga izquierda","desc_hacia":"lado izquierdo de la oruga derecha","tipo":"ENCAJE"}
  ]
}
```

### `data/puzzles/monsters.json`
```json
{
  "puzzle": {
    "id": "puzzle_monsters", "nombre": "Monsters Creatures", "tipo": "LIBRE",
    "marca": "Desconocida", "material": "Madera/Foam",
    "tema": "Criaturas fantasticas", "tiene_bandeja": false
  },
  "clusters": [
    {
      "id": "cluster_monsters_A", "puzzle_id": "puzzle_monsters",
      "nombre_cluster": "Criatura morada", "total_piezas": 3,
      "piezas": [
        {"id":"mo_1","cluster_id":"cluster_monsters_A","numero_etiqueta":1,"descripcion_visual":"Parte superior cabeza morada redonda","disponible":true,"fila":null,"columna":null},
        {"id":"mo_2","cluster_id":"cluster_monsters_A","numero_etiqueta":2,"descripcion_visual":"Parte inferior cabeza morada redonda","disponible":true,"fila":null,"columna":null},
        {"id":"mo_3","cluster_id":"cluster_monsters_A","numero_etiqueta":3,"descripcion_visual":"Lengua/cola roja curva","disponible":true,"fila":null,"columna":null}
      ]
    },
    {
      "id": "cluster_monsters_B", "puzzle_id": "puzzle_monsters",
      "nombre_cluster": "Monstruo verde-rojo", "total_piezas": 4,
      "piezas": [
        {"id":"mo_4","cluster_id":"cluster_monsters_B","numero_etiqueta":4,"descripcion_visual":"Cuerpo superior verde con brazos y ojos","disponible":true,"fila":null,"columna":null},
        {"id":"mo_5","cluster_id":"cluster_monsters_B","numero_etiqueta":5,"descripcion_visual":"Cuerpo inferior rojo","disponible":true,"fila":null,"columna":null},
        {"id":"mo_6","cluster_id":"cluster_monsters_B","numero_etiqueta":6,"descripcion_visual":"Pierna izquierda azul","disponible":true,"fila":null,"columna":null},
        {"id":"mo_7","cluster_id":"cluster_monsters_B","numero_etiqueta":7,"descripcion_visual":"Pierna derecha azul","disponible":true,"fila":null,"columna":null}
      ]
    },
    {
      "id": "cluster_monsters_C", "puzzle_id": "puzzle_monsters",
      "nombre_cluster": "Rana verde", "total_piezas": 6,
      "piezas": [
        {"id":"mo_8","cluster_id":"cluster_monsters_C","numero_etiqueta":8,"descripcion_visual":"Ojo izquierdo blanco/negro","disponible":true,"fila":null,"columna":null},
        {"id":"mo_9","cluster_id":"cluster_monsters_C","numero_etiqueta":9,"descripcion_visual":"Ojo derecho blanco/negro","disponible":true,"fila":null,"columna":null},
        {"id":"mo_10","cluster_id":"cluster_monsters_C","numero_etiqueta":10,"descripcion_visual":"Cabeza verde de la rana","disponible":true,"fila":null,"columna":null},
        {"id":"mo_11","cluster_id":"cluster_monsters_C","numero_etiqueta":11,"descripcion_visual":"Cuerpo central morado/azul","disponible":true,"fila":null,"columna":null},
        {"id":"mo_12","cluster_id":"cluster_monsters_C","numero_etiqueta":12,"descripcion_visual":"Pata/brazo izquierdo verde","disponible":true,"fila":null,"columna":null},
        {"id":"mo_13","cluster_id":"cluster_monsters_C","numero_etiqueta":13,"descripcion_visual":"Pata/brazo derecho verde","disponible":true,"fila":null,"columna":null}
      ]
    }
  ],
  "conexiones": [
    {"origen":"mo_1","destino":"mo_2","desc_desde":"parte inferior de la cabeza superior","desc_hacia":"parte superior de la cabeza inferior","tipo":"ENCAJE"},
    {"origen":"mo_2","destino":"mo_3","desc_desde":"parte inferior de la cabeza","desc_hacia":"extremo superior de la lengua","tipo":"ENCAJE"},
    {"origen":"mo_4","destino":"mo_5","desc_desde":"parte inferior del cuerpo verde","desc_hacia":"parte superior del cuerpo rojo","tipo":"ENCAJE"},
    {"origen":"mo_5","destino":"mo_6","desc_desde":"extremo inferior izquierdo del cuerpo","desc_hacia":"parte superior de la pierna izquierda","tipo":"ENCAJE"},
    {"origen":"mo_5","destino":"mo_7","desc_desde":"extremo inferior derecho del cuerpo","desc_hacia":"parte superior de la pierna derecha","tipo":"ENCAJE"},
    {"origen":"mo_8","destino":"mo_10","desc_desde":"base del ojo izquierdo","desc_hacia":"ranura ojo izquierdo de la cabeza","tipo":"ENCAJE"},
    {"origen":"mo_9","destino":"mo_10","desc_desde":"base del ojo derecho","desc_hacia":"ranura ojo derecho de la cabeza","tipo":"ENCAJE"},
    {"origen":"mo_10","destino":"mo_11","desc_desde":"parte inferior de la cabeza","desc_hacia":"parte superior del cuerpo","tipo":"ENCAJE"},
    {"origen":"mo_11","destino":"mo_12","desc_desde":"lado izquierdo del cuerpo","desc_hacia":"extremo del brazo/pata izquierda","tipo":"ENCAJE"},
    {"origen":"mo_11","destino":"mo_13","desc_desde":"lado derecho del cuerpo","desc_hacia":"extremo del brazo/pata derecha","tipo":"ENCAJE"}
  ]
}
```

### `data/puzzles/dolphins.json` (plantilla — completar conexiones)
```json
{
  "puzzle": {
    "id": "puzzle_dolphins", "nombre": "Dolphins Family", "tipo": "BANDEJA",
    "marca": "Desconocida", "material": "Madera",
    "tema": "Animales marinos", "tiene_bandeja": true
  },
  "clusters": [{
    "id": "cluster_dolphins_1", "puzzle_id": "puzzle_dolphins",
    "nombre_cluster": "Familia de delfines y ballena", "total_piezas": 9,
    "piezas": [
      "TODO: numerar y describir las 9 piezas (ballena azul, delfin turquesa, delfin rosa). Las piezas NO tienen numero fisico, asignar IDs do_1..do_9"
    ]
  }],
  "conexiones": [
    "TODO: este puzzle es tipo BANDEJA con SOLAPE entre figuras. Confirmar adyacencias reales antes de cargar."
  ]
}
```

### `data/puzzles/city_grid.json` (plantilla — usar coordenadas reales)
```json
{
  "puzzle": {
    "id": "puzzle_city", "nombre": "City Airplane Scene", "tipo": "GRID",
    "marca": "Desconocida", "material": "Carton",
    "tema": "Ciudad con avion", "tiene_bandeja": true
  },
  "clusters": [{
    "id": "cluster_city_1", "puzzle_id": "puzzle_city",
    "nombre_cluster": "Escena completa", "total_piezas": 24,
    "piezas": [
      "TODO: este puzzle YA tiene coordenadas (fila,columna) escritas en masking tape, de (0,0) a (3,5). Generar piezas con fila/columna y las conexiones se derivan automaticamente de la cuadricula (ver nota abajo)."
    ]
  }],
  "conexiones": [
    "TODO: para GRID, generar conexiones programaticamente: cada (f,c) conecta con (f,c+1) [derecha] y (f+1,c) [abajo]."
  ]
}
```

> **Nota para el GRID:** como este puzzle es regular, conviene un generador. Para cada pieza `(f,c)`, crear conexión a `(f,c+1)` con `desc_desde="lado derecho"`, `desc_hacia="lado izquierdo"`, y a `(f+1,c)` con `desc_desde="lado inferior"`, `desc_hacia="lado superior"`. Esto se puede hacer en un pequeño script `generar_grid.py`.

---

## 8. Consultas útiles en Neo4j Browser (para la demo)

```cypher
// Ver un puzzle completo con sus clusters y piezas
MATCH (p:Puzzle {id:'puzzle_excavator'})<-[:PERTENECE_A]-(c:Cluster)<-[:PERTENECE_A]-(pz:Pieza)
RETURN p, c, pz;

// Ver solo el grafo de conexiones de un cluster
MATCH (a:Pieza {cluster_id:'cluster_excavator_1'})-[r:CONECTA_CON]->(b:Pieza)
RETURN a, r, b;

// Listar piezas faltantes
MATCH (p:Pieza {disponible:false})
RETURN p.id, p.numero_etiqueta, p.descripcion_visual;

// Contar clusters por puzzle (demostrar multi-cluster)
MATCH (c:Cluster)-[:PERTENECE_A]->(p:Puzzle)
RETURN p.nombre, count(c) AS num_clusters;
```

---

## 9. Orden de construcción para Claude Code

1. Crear estructura de carpetas y `requirements.txt`, `.env.example`, `.gitignore`.
2. Implementar `src/db.py` y probar conexión (`python -m src.db` o menú opción 1).
3. Implementar `src/schema.py` y aplicar constraints.
4. Crear los JSON de `excavator` y `monsters` (datos completos arriba).
5. Implementar `src/loader.py` y cargar los puzzles.
6. Verificar carga en Neo4j Aura Browser con las consultas de la sección 8.
7. Implementar `src/missing.py`.
8. Implementar `src/solver.py` (BFS con manejo de faltantes).
9. Implementar `src/main.py` (CLI).
10. Completar `dolphins.json` y `city_grid.json` (requiere confirmar adyacencias).
11. Escribir `tests/test_solver.py` (casos: armado completo, con 1 pieza faltante, pieza inicial inexistente).
12. Escribir `README.md` con instrucciones de uso.

---

## 10. Cobertura de la rúbrica

| Aspecto rúbrica | % | Cómo lo cubre esta solución |
|---|---|---|
| Justificación de BD | 10 | Sección 0: tabla comparativa Neo4j vs SQL |
| Diseño del modelo | 20 | Sección 5: nodos, relaciones, clusters, piezas faltantes, escalable |
| Implementación + poblado | 10 | Loader + JSON de puzzles reales |
| Explicación del algoritmo | 10 | BFS documentado: entradas, salidas, uso de la BD |
| Armado sin faltantes | 20 | `solver.py` recorre el grafo desde pieza inicial |
| Armado con faltantes | 20 | `solver.py` emite advertencia y continúa; resumen final |
| Presentación | 10 | Demo con Neo4j Browser (grafo visual) + CLI en vivo |

---

## 11. Puntos a confirmar antes de cargar (importante)

- **Conexiones del excavator y monsters:** fueron inferidas de las fotos. Verificar físicamente armando el rompecabezas real y ajustar el JSON si alguna adyacencia difiere.
- **Delfines:** confirmar cómo se numeran/dividen las 9 piezas y su solape.
- **Grid (ciudad):** usar las coordenadas reales escritas en masking tape; generar conexiones con el script de cuadrícula.
- **Demo de tiempo:** la presentación no debe exceder 15 min (penalización a los 20). Preparar 2-3 corridas: armado completo, armado con pieza faltante, y mostrar el grafo en Aura Browser.
