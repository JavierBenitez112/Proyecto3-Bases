# Paquete de Datos 2 — Poblado de Rompecabezas

**Complemento de:** `PLAN_IMPLEMENTACION.md`
**Objetivo:** Agregar y poblar 4 rompecabezas nuevos/pendientes en la base de datos Neo4j Aura del proyecto.

---

## 0. Qué cubre este documento

| Rompecabezas | Imagen | Estado | Tipo | Piezas | Clusters |
|---|---|---|---|---|---|
| Plesiosaurs (dinosaurio) | 1 | **NUEVO** | LIBRE (bandeja) | 10 | 1 |
| Ciudad con avión | 2 | Completar | GRID | 24 (4×6) | 1 |
| Delfines + ballena | 3 | Completar | BANDEJA | 9 | 3 |
| Animales/osos | 4 | **NUEVO** | GRID | por contar | 1 |

> **Ya implementados (ignorar):** Excavator (imagen 5) y Monsters (imagen 6) están en `PLAN_IMPLEMENTACION.md`.

Estos archivos van en `data/puzzles/` y se cargan con el `loader.py` ya existente. No se cambia ningún módulo; solo se agregan datos.

---

## 1. Plesiosaurs (dinosaurio) — `data/puzzles/plesiosaurs.json`

**Análisis de la foto:** rompecabezas de madera con bandeja, 10 piezas numeradas. La pieza 1 es la cabeza (sin número visible por el ángulo, pero es la pieza inicial lógica). El cuello baja (2 → 3) hacia el cuerpo. El cuerpo se recorre de derecha a izquierda (4 → 5 → 6 → 7 → 8). La cola está arriba a la izquierda (10) y la pata abajo a la izquierda (9).

```json
{
  "puzzle": {
    "id": "puzzle_plesiosaurs", "nombre": "Plesiosaurs", "tipo": "LIBRE",
    "marca": "Desconocida", "material": "Madera",
    "tema": "Dinosaurio acuatico", "tiene_bandeja": true
  },
  "clusters": [{
    "id": "cluster_plesiosaurs_1", "puzzle_id": "puzzle_plesiosaurs",
    "nombre_cluster": "Plesiosaurio completo", "total_piezas": 10,
    "piezas": [
      {"id":"pl_1","cluster_id":"cluster_plesiosaurs_1","numero_etiqueta":1,"descripcion_visual":"Cabeza con ojos (arriba a la derecha)","disponible":true,"fila":null,"columna":null},
      {"id":"pl_2","cluster_id":"cluster_plesiosaurs_1","numero_etiqueta":2,"descripcion_visual":"Cuello superior","disponible":true,"fila":null,"columna":null},
      {"id":"pl_3","cluster_id":"cluster_plesiosaurs_1","numero_etiqueta":3,"descripcion_visual":"Cuello inferior (base del cuello)","disponible":true,"fila":null,"columna":null},
      {"id":"pl_4","cluster_id":"cluster_plesiosaurs_1","numero_etiqueta":4,"descripcion_visual":"Cuerpo extremo derecho (grupa)","disponible":true,"fila":null,"columna":null},
      {"id":"pl_5","cluster_id":"cluster_plesiosaurs_1","numero_etiqueta":5,"descripcion_visual":"Cuerpo centro-derecha (lomo)","disponible":true,"fila":null,"columna":null},
      {"id":"pl_6","cluster_id":"cluster_plesiosaurs_1","numero_etiqueta":6,"descripcion_visual":"Cuerpo centro","disponible":true,"fila":null,"columna":null},
      {"id":"pl_7","cluster_id":"cluster_plesiosaurs_1","numero_etiqueta":7,"descripcion_visual":"Cuerpo centro-izquierda (vientre)","disponible":true,"fila":null,"columna":null},
      {"id":"pl_8","cluster_id":"cluster_plesiosaurs_1","numero_etiqueta":8,"descripcion_visual":"Cuerpo izquierdo (pecho)","disponible":true,"fila":null,"columna":null},
      {"id":"pl_9","cluster_id":"cluster_plesiosaurs_1","numero_etiqueta":9,"descripcion_visual":"Pata/aleta inferior izquierda","disponible":true,"fila":null,"columna":null},
      {"id":"pl_10","cluster_id":"cluster_plesiosaurs_1","numero_etiqueta":10,"descripcion_visual":"Cola superior izquierda (curva)","disponible":true,"fila":null,"columna":null}
    ]
  }],
  "conexiones": [
    {"origen":"pl_1","destino":"pl_2","desc_desde":"base de la cabeza","desc_hacia":"extremo superior del cuello","tipo":"ENCAJE"},
    {"origen":"pl_2","destino":"pl_3","desc_desde":"parte inferior del cuello superior","desc_hacia":"parte superior del cuello inferior","tipo":"ENCAJE"},
    {"origen":"pl_3","destino":"pl_5","desc_desde":"base del cuello","desc_hacia":"parte superior derecha del lomo","tipo":"ENCAJE"},
    {"origen":"pl_5","destino":"pl_4","desc_desde":"lado derecho del lomo","desc_hacia":"lado izquierdo de la grupa","tipo":"ENCAJE"},
    {"origen":"pl_5","destino":"pl_6","desc_desde":"lado izquierdo del lomo","desc_hacia":"lado derecho del cuerpo centro","tipo":"ENCAJE"},
    {"origen":"pl_6","destino":"pl_7","desc_desde":"lado izquierdo del cuerpo centro","desc_hacia":"lado derecho del vientre","tipo":"ENCAJE"},
    {"origen":"pl_7","destino":"pl_8","desc_desde":"lado izquierdo del vientre","desc_hacia":"lado derecho del pecho","tipo":"ENCAJE"},
    {"origen":"pl_8","destino":"pl_10","desc_desde":"parte superior del pecho","desc_hacia":"base de la cola","tipo":"ENCAJE"},
    {"origen":"pl_8","destino":"pl_9","desc_desde":"parte inferior del pecho","desc_hacia":"parte superior de la pata","tipo":"ENCAJE"}
  ]
}
```

> **Verificar físicamente:** las uniones del cuello al cuerpo (`pl_3`→`pl_5`) y de la cola/pata (`pl_8`→`pl_10`, `pl_8`→`pl_9`) son las más inciertas por el ángulo de la foto. Armar el dinosaurio real y ajustar si difiere.

---

## 2. Delfines + ballena — `data/puzzles/dolphins.json`

**Análisis de la foto:** rompecabezas de madera con bandeja. Son **3 figuras independientes** (no se ensamblan entre sí, solo comparten la bandeja), por eso se modelan como **3 clusters**. Las piezas no tienen número físico, así que se asignan IDs internos `do_*`.

- Delfín turquesa (arriba izquierda): ~3 piezas
- Delfín rosa (arriba derecha): ~3 piezas
- Ballena azul (centro/abajo): ~3 piezas

```json
{
  "puzzle": {
    "id": "puzzle_dolphins", "nombre": "Dolphins Family", "tipo": "BANDEJA",
    "marca": "Desconocida", "material": "Madera",
    "tema": "Animales marinos", "tiene_bandeja": true
  },
  "clusters": [
    {
      "id": "cluster_dolphins_turquesa", "puzzle_id": "puzzle_dolphins",
      "nombre_cluster": "Delfin turquesa", "total_piezas": 3,
      "piezas": [
        {"id":"do_t1","cluster_id":"cluster_dolphins_turquesa","numero_etiqueta":null,"descripcion_visual":"Cabeza delfin turquesa","disponible":true,"fila":null,"columna":null},
        {"id":"do_t2","cluster_id":"cluster_dolphins_turquesa","numero_etiqueta":null,"descripcion_visual":"Cuerpo delfin turquesa","disponible":true,"fila":null,"columna":null},
        {"id":"do_t3","cluster_id":"cluster_dolphins_turquesa","numero_etiqueta":null,"descripcion_visual":"Cola delfin turquesa","disponible":true,"fila":null,"columna":null}
      ]
    },
    {
      "id": "cluster_dolphins_rosa", "puzzle_id": "puzzle_dolphins",
      "nombre_cluster": "Delfin rosa", "total_piezas": 3,
      "piezas": [
        {"id":"do_r1","cluster_id":"cluster_dolphins_rosa","numero_etiqueta":null,"descripcion_visual":"Cabeza delfin rosa","disponible":true,"fila":null,"columna":null},
        {"id":"do_r2","cluster_id":"cluster_dolphins_rosa","numero_etiqueta":null,"descripcion_visual":"Cuerpo delfin rosa","disponible":true,"fila":null,"columna":null},
        {"id":"do_r3","cluster_id":"cluster_dolphins_rosa","numero_etiqueta":null,"descripcion_visual":"Cola delfin rosa","disponible":true,"fila":null,"columna":null}
      ]
    },
    {
      "id": "cluster_dolphins_ballena", "puzzle_id": "puzzle_dolphins",
      "nombre_cluster": "Ballena azul", "total_piezas": 3,
      "piezas": [
        {"id":"do_b1","cluster_id":"cluster_dolphins_ballena","numero_etiqueta":null,"descripcion_visual":"Cabeza ballena azul","disponible":true,"fila":null,"columna":null},
        {"id":"do_b2","cluster_id":"cluster_dolphins_ballena","numero_etiqueta":null,"descripcion_visual":"Cuerpo ballena azul","disponible":true,"fila":null,"columna":null},
        {"id":"do_b3","cluster_id":"cluster_dolphins_ballena","numero_etiqueta":null,"descripcion_visual":"Cola ballena azul","disponible":true,"fila":null,"columna":null}
      ]
    }
  ],
  "conexiones": [
    {"origen":"do_t1","destino":"do_t2","desc_desde":"parte trasera de la cabeza turquesa","desc_hacia":"parte frontal del cuerpo turquesa","tipo":"ENCAJE"},
    {"origen":"do_t2","destino":"do_t3","desc_desde":"parte trasera del cuerpo turquesa","desc_hacia":"base de la cola turquesa","tipo":"ENCAJE"},
    {"origen":"do_r1","destino":"do_r2","desc_desde":"parte trasera de la cabeza rosa","desc_hacia":"parte frontal del cuerpo rosa","tipo":"ENCAJE"},
    {"origen":"do_r2","destino":"do_r3","desc_desde":"parte trasera del cuerpo rosa","desc_hacia":"base de la cola rosa","tipo":"ENCAJE"},
    {"origen":"do_b1","destino":"do_b2","desc_desde":"parte trasera de la cabeza de la ballena","desc_hacia":"parte frontal del cuerpo de la ballena","tipo":"ENCAJE"},
    {"origen":"do_b2","destino":"do_b3","desc_desde":"parte trasera del cuerpo de la ballena","desc_hacia":"base de la cola de la ballena","tipo":"ENCAJE"}
  ]
}
```

> **Verificar físicamente:** confirmar cuántas piezas tiene cada figura realmente (estimé 3 por figura = 9 total). Si alguna figura tiene 2 o 4 piezas, ajustar el cluster y sus conexiones. Como las figuras no se ensamblan entre sí, cada cluster armará su propia figura por separado — esto demuestra perfectamente el manejo multi-cluster ante el docente.

---

## 3. Grids (Ciudad y Animales) — generador automático

Los puzzles tipo cuadrícula (imágenes 2 y 4) tienen demasiadas piezas para escribir conexiones a mano. Como son regulares, conviene **generarlos por código**. Cada pieza `(fila, columna)` se conecta con su vecina derecha `(fila, columna+1)` y su vecina inferior `(fila+1, columna)`. El loader luego las hace bidireccionales.

### `src/generar_grid.py`

```python
import json, os

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
            # vecina derecha
            if c + 1 < columnas:
                conexiones.append({
                    "origen": origen, "destino": f"{prefijo}_{f}_{c+1}",
                    "desc_desde": "lado derecho", "desc_hacia": "lado izquierdo",
                    "tipo": "ENCAJE"
                })
            # vecina inferior
            if f + 1 < filas:
                conexiones.append({
                    "origen": origen, "destino": f"{prefijo}_{f+1}_{c}",
                    "desc_desde": "lado inferior", "desc_hacia": "lado superior",
                    "tipo": "ENCAJE"
                })

    data = {
        "puzzle": {
            "id": puzzle_id, "nombre": nombre, "tipo": "GRID",
            "marca": marca, "material": material, "tema": tema,
            "tiene_bandeja": tiene_bandeja
        },
        "clusters": [{
            "id": cluster_id, "puzzle_id": puzzle_id,
            "nombre_cluster": "Escena completa",
            "total_piezas": filas * columnas,
            "piezas": piezas
        }],
        "conexiones": conexiones
    }

    os.makedirs("data/puzzles", exist_ok=True)
    ruta = f"data/puzzles/{puzzle_id}.json"
    with open(ruta, "w", encoding="utf-8") as fp:
        json.dump(data, fp, ensure_ascii=False, indent=2)
    print(f"✅ Generado {ruta} — {filas}x{columnas} = {filas*columnas} piezas")


if __name__ == "__main__":
    # ── IMAGEN 2: Ciudad con avion (coordenadas (0,0) a (3,5)) ──
    generar_grid(
        puzzle_id="puzzle_city",
        nombre="City Airplane Scene",
        tema="Ciudad con avion",
        filas=4, columnas=6,        # VERIFICAR: la fila 3 puede estar incompleta
        material="Carton", prefijo="ci"
    )

    # ── IMAGEN 4: Animales/osos (jigsaw sin etiquetas) ──
    # CONTAR filas y columnas reales en la pieza fisica y ajustar aqui.
    generar_grid(
        puzzle_id="puzzle_bears",
        nombre="Animals Scene",
        tema="Animales de bosque",
        filas=5, columnas=6,        # ESTIMADO: contar piezas reales y corregir
        material="Carton", prefijo="be"
    )
```

### Cómo usarlo

```bash
python -m src.generar_grid     # crea data/puzzles/puzzle_city.json y puzzle_bears.json
python -m src.loader           # carga TODOS los JSON (incluidos los nuevos)
```

> **Importante sobre las dimensiones:**
> - **Ciudad (imagen 2):** las coordenadas escritas van de `(0,0)` a `(3,5)`. Eso sugiere 4 filas × 6 columnas = 24 piezas. Pero en la foto la fila 3 (inferior) parece incompleta. **Contar las piezas reales de la fila inferior** y, si la cuadrícula no es rectangular perfecta, eliminar del JSON las piezas que no existan y sus conexiones.
> - **Animales/osos (imagen 4):** no tiene etiquetas y está fotografiado de cabeza. **Contar filas y columnas físicas** antes de generar. Dejé 5×6 como estimación.

---

## 4. Orden de ejecución para poblar la base

Asumiendo que `PLAN_IMPLEMENTACION.md` ya está construido y la conexión a Aura funciona:

1. Colocar `plesiosaurs.json` y `dolphins.json` en `data/puzzles/`.
2. Crear `src/generar_grid.py` (código arriba).
3. Ajustar las dimensiones de los grids según conteo físico.
4. Ejecutar el generador:
   ```bash
   python -m src.generar_grid
   ```
5. Cargar todo a Neo4j Aura:
   ```bash
   python -m src.loader
   ```
6. Verificar en Neo4j Aura Browser:
   ```cypher
   MATCH (p:Puzzle) RETURN p.id, p.nombre, p.tipo;
   ```
   Deberían aparecer: `puzzle_excavator`, `puzzle_monsters`, `puzzle_plesiosaurs`, `puzzle_dolphins`, `puzzle_city`, `puzzle_bears`.

7. Probar el solver con una pieza de cada tipo:
   ```bash
   python -m src.main      # opción 7, probar con: pl_1, do_t1, ci_0_0, be_0_0
   ```

---

## 5. Consultas de verificación por puzzle

```cypher
-- Plesiosaurs: ver el grafo del dinosaurio
MATCH (a:Pieza {cluster_id:'cluster_plesiosaurs_1'})-[r:CONECTA_CON]->(b:Pieza)
RETURN a, r, b;

-- Delfines: demostrar los 3 clusters separados
MATCH (c:Cluster)-[:PERTENECE_A]->(p:Puzzle {id:'puzzle_dolphins'})
RETURN c.nombre_cluster, c.total_piezas;

-- Ciudad: ver la cuadricula y sus coordenadas
MATCH (p:Pieza)-[:PERTENECE_A]->(:Cluster {id:'cluster_puzzle_city_1'})
RETURN p.id, p.fila, p.columna ORDER BY p.fila, p.columna;

-- Conteo global de piezas por puzzle
MATCH (pz:Pieza)-[:PERTENECE_A]->(:Cluster)-[:PERTENECE_A]->(p:Puzzle)
RETURN p.nombre, count(pz) AS total_piezas ORDER BY p.nombre;
```

---

## 6. Checklist de verificación física (antes de la demo)

- [ ] **Plesiosaurs:** armar el dinosaurio y confirmar uniones cuello-cuerpo y cola/pata.
- [ ] **Delfines:** contar piezas reales de cada figura (turquesa, rosa, ballena).
- [ ] **Ciudad:** confirmar si la cuadrícula es 4×6 completa o la fila inferior está incompleta.
- [ ] **Animales/osos:** contar filas × columnas reales y corregir el generador.
- [ ] Probar `solver` con una pieza inicial de cada puzzle nuevo.
- [ ] Probar marcar una pieza faltante en cada puzzle (`opción 4` del menú) y ver la advertencia.

---

## 7. Nota de diseño para la presentación

Estos 4 puzzles refuerzan tres argumentos fuertes ante la rúbrica:

1. **Escalabilidad real:** el mismo modelo (Puzzle → Cluster → Pieza → CONECTA_CON) representó sin cambios un dinosaurio irregular, delfines en bandeja, y dos cuadrículas. No se modificó ni un módulo de código para agregarlos.
2. **Multi-cluster demostrado dos veces:** Monsters (3 criaturas) y Delfines (3 figuras) prueban que el sistema maneja varios sub-rompecabezas independientes en un mismo set.
3. **Dos paradigmas, un solo algoritmo:** los puzzles LIBRE/BANDEJA (grafo irregular) y los GRID (cuadrícula) se resuelven con el **mismo BFS**, porque ambos terminan siendo el mismo tipo de grafo en la base de datos.
