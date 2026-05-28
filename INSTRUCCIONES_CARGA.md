# Instrucciones para Cargar Puzzles a Neo4j Aura

Documento que guía el poblado completo de la base de datos con los 6 rompecabezas.

---

## Estado Actual

Todos los JSONs de puzzles estan listos en `data/puzzles/`:

- excavator.json (2 piezas)
- monsters.json (13 piezas, 3 clusters)
- plesiosaurs.json (10 piezas) - NUEVO
- dolphins.json (9 piezas, 3 clusters) - NUEVO
- puzzle_city.json (24 piezas, grid 4x6) - NUEVO (AUTOGENERADO)
- puzzle_bears.json (30 piezas, grid 5x6) - NUEVO (AUTOGENERADO)

**Total: 96 piezas en 8 clusters**

---

## Paso 1: Verificar conexion a Neo4j Aura

Asegurate que tienes configuradas las credenciales en `.env` con los datos de tu instancia Neo4j Aura.

```bash
python3 -m src.main
# Seleccionar opcion 1: Verificar conexion
```

Salida esperada:
```
Conexion a Neo4j Aura exitosa.
```

---

## Paso 2: Aplicar schema (constraints)

Esto crea las restricciones de unicidad para los IDs de Puzzles, Clusters y Piezas.

```bash
python3 -m src.main
# Seleccionar opcion 2: Aplicar schema
```

Salida esperada:
```
Constraints aplicados.
```

---

## Paso 3: Cargar todos los puzzles

```bash
python3 -m src.main
# Seleccionar opcion 3: Cargar todos los puzzles
```

Salida esperada:
```
Cargado: Excavator
Cargado: Monsters Creatures
Cargado: Plesiosaurs
Cargado: Dolphins Family
Cargado: City Airplane Scene
Cargado: Animals Scene
```

---

## Paso 4: Verificar en Neo4j Browser

Abre Neo4j Aura Browser en https://auradb.neo4j.io/ con tus credenciales.

### Consulta 1: Ver todos los puzzles

```cypher
MATCH (p:Puzzle)
RETURN p.id, p.nombre, p.tipo, count(distinct c) AS clusters
ORDER BY p.nombre;
```

Salida esperada: 6 puzzles con sus tipos (LIBRE, BANDEJA, GRID)

### Consulta 2: Contar total de piezas por puzzle

```cypher
MATCH (pz:Pieza)-[:PERTENECE_A]->(:Cluster)-[:PERTENECE_A]->(p:Puzzle)
RETURN p.nombre, count(pz) AS total_piezas
ORDER BY p.nombre;
```

Salida esperada:
- Animals Scene: 30
- City Airplane Scene: 24
- Dolphins Family: 9
- Excavator: 10
- Monsters Creatures: 13
- Plesiosaurs: 10

### Consulta 3: Demostrar multi-cluster

```cypher
MATCH (c:Cluster)-[:PERTENECE_A]->(p:Puzzle)
WHERE p.nombre IN ['Monsters Creatures', 'Dolphins Family']
RETURN p.nombre, collect(c.nombre_cluster) AS clusters;
```

Salida esperada:
- Monsters Creatures: 3 clusters
- Dolphins Family: 3 clusters

### Consulta 4: Visualizar el grafo de Plesiosaurs

```cypher
MATCH (a:Pieza {cluster_id:'cluster_plesiosaurs_1'})-[r:CONECTA_CON]->(b:Pieza)
RETURN a, r, b;
```

Muestra: dinosaurio como grafo conectado (cabeza -> cuello -> cuerpo -> cola/pata)

### Consulta 5: Visualizar la cuadricula de City

```cypher
MATCH (p:Pieza {cluster_id:'cluster_puzzle_city_1'})
RETURN p.id, p.fila, p.columna
ORDER BY p.fila, p.columna;
```

Muestra: 24 piezas en coordenadas (0,0) a (3,5)

---

## Paso 5: Probar el Solver con diferentes puzzles

### Test 1: Excavator (lineal simple)

```bash
python3 -m src.main
# Opcion 7: Armar rompecabezas
# Pieza inicial: ex_1
```

Verifica: camino ex_1 -> ex_2 -> ex_3 -> ... -> ex_10

### Test 2: Monsters (multi-cluster)

```bash
python3 -m src.main
# Opcion 7: Armar rompecabezas
# Pieza inicial: mo_1
```

Verifica: grafo que recorre solo el cluster A (mo_1 -> mo_2 -> mo_3)

Luego intenta con `mo_4` (cluster B) y `mo_8` (cluster C).

### Test 3: Plesiosaurs (irregular)

```bash
python3 -m src.main
# Opcion 7: Armar rompecabezas
# Pieza inicial: pl_1
```

Verifica: camino pl_1 -> pl_2 -> pl_3 -> pl_5 -> ... (no lineal)

### Test 4: Dolphins (3 clusters BANDEJA)

```bash
python3 -m src.main
# Opcion 7: Armar rompecabezas
# Pieza inicial: do_t1
```

Verifica: solo arma el cluster turquesa (do_t1 -> do_t2 -> do_t3)

Luego prueba con `do_r1` (cluster rosa) y `do_b1` (cluster ballena).

### Test 5: City (grid regular)

```bash
python3 -m src.main
# Opcion 7: Armar rompecabezas
# Pieza inicial: ci_0_0
```

Verifica: recorrido BFS desde (0,0) que alcanza todas las piezas de la cuadricula

### Test 6: Animals (grid grande)

```bash
python3 -m src.main
# Opcion 7: Armar rompecabezas
# Pieza inicial: be_0_0
```

Verifica: recorrido de 30 piezas (5x6 grid)

---

## Paso 6: Probar manejo de piezas faltantes

```bash
python3 -m src.main
# Opcion 4: Marcar pieza como faltante
# Pieza: ex_5
# Opcion 7: Armar rompecabezas
# Pieza inicial: ex_1
```

Verifica:
- Detecta que ex_5 falta
- Emite advertencia
- Continua recorriendo y llega a ex_6 (vecino de ex_5)
- Al final muestra "1 pieza(s) faltante(s)"

---

## Paso 7: Reset y limpieza

```bash
python3 -m src.main
# Opcion 6: Reset (todas disponibles)
```

Restaura todas las piezas a estado disponible = true

---

## Checklist de Demo Final

- [ ] Neo4j Browser muestra 6 puzzles
- [ ] Total de 96 piezas contadas correctamente
- [ ] Consultas de multi-cluster funcionan (Monsters y Dolphins)
- [ ] Solver funciona desde al menos 3 puzzles diferentes
- [ ] Manejo de piezas faltantes emite advertencia y continua
- [ ] Grid (City) recorre 24 piezas sin problemas
- [ ] Grid (Animals) recorre 30 piezas sin problemas

---

## Notas para la Presentacion

**Argumentos fuertes de la arquitectura:**

1. **Escalabilidad sin cambios de codigo:** Se agregaron 3 puzzles nuevos (Plesiosaurs, Dolphins, City, Animals) SIN modificar ni un modulo de Python. El mismo modelo Puzzle -> Cluster -> Pieza -> CONECTA_CON funciono perfectamente.

2. **Multi-cluster demostrado dos veces:** Monsters (3 criaturas) y Dolphins (3 figuras) prueban independencia real entre sub-rompecabezas en un mismo set.

3. **Dos paradigmas, un algoritmo:** Puzzles irregulares (LIBRE) y cuadriculados (GRID) se resuelven con el MISMO BFS porque ambos son grafos en la BD.

4. **Autogeneracion de datos:** El script generar_grid.py demuestra que la estructura es tan flexible que permite generar datos complejos sin hardcoding.

---

## Diagnosticos

Si encuentras errores:

### Error: "No existe la pieza 'xxx'"

- Verificar que el ID de la pieza es correcto
- Usar el prefijo correcto: ex_, mo_, pl_, do_t/r/b, ci_, be_

### Error: "La pieza inicial xxx no esta disponible" + solver no continua

- Probablemente marcaste esa pieza como faltante
- Ejecuta opcion 6 (Reset) para restaurar

### Error: Cargar puzzles falla

- Verifica la conexion a Neo4j (opcion 1)
- Comprueba que el archivo .env tiene credenciales validas
- Asegúrate que la instancia Neo4j esta en estado "Running"

### Error: Neo4j Browser no muestra nodos

- Espera a que termine la carga (puede tomar 10-30 segundos)
- Presiona Ctrl+R en el browser para refrescar
- Ejecuta `MATCH (p) RETURN count(p)` para contar nodos totales

---

## Linea de Tiempo Estimada

- Paso 1: 10 segundos
- Paso 2: 30 segundos
- Paso 3 (carga): 30-60 segundos
- Paso 4 (verificacion en browser): 2-3 minutos
- Paso 5 (tests del solver): 5-10 minutos
- Paso 6 (faltantes): 3-5 minutos

**Total: 15-25 minutos para demo completa**
