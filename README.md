# Rompecabezas BD2 - Sistema de Armado con Neo4j

Sistema inteligente para armar rompecabezas fisicos no convencionales utilizando una base de datos de grafos (Neo4j Aura).

## Descripcion

Este proyecto modela rompecabezas como grafos donde:
- **Nodos** representan piezas individuales
- **Relaciones** representan conexiones fisicas entre piezas
- **Clusters** soportan multiples sub-rompecabezas independientes dentro del mismo set
- **Piezas faltantes** son manejadas inteligentemente por el algoritmo

El sistema genera guias paso-a-paso para armar cualquier rompecabeza desde una pieza inicial, utilizando busqueda BFS para encontrar el camino optimo.

## Requisitos

- Python 3.10+
- Cuenta gratuita en Neo4j Aura (https://neo4j.com/product/auradb/)
- Credenciales de la instancia Neo4j Aura

## Instalacion

1. Clonar o descargar el proyecto:
```bash
cd Proyecto3
```

2. Crear entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar credenciales:
   - Copiar `.env.example` a `.env`
   - Rellenar con credenciales de Neo4j Aura:
     - `NEO4J_URI`: URI de la instancia (formato neo4j+s://xxxx.databases.neo4j.io)
     - `NEO4J_USERNAME`: Usuario (normalmente "neo4j")
     - `NEO4J_PASSWORD`: Contraseña

5. Crear instancia Neo4j Aura:
   - Ir a https://neo4j.com/product/auradb/
   - Crear cuenta gratuita
   - Crear instancia AuraDB Free
   - Guardar credenciales en `.env`
   - Esperar a que el estado sea "Running"

## Uso

Ejecutar el menu interactivo:
```bash
python -m src.main
```

### Opciones del Menu

1. **Verificar conexion** - Prueba conexion a Neo4j Aura
2. **Aplicar schema** - Crea constraints de unicidad
3. **Cargar puzzles** - Importa todos los puzzles desde JSON
4. **Marcar pieza faltante** - Marca una pieza como no disponible
5. **Restaurar pieza** - Marca una pieza como disponible nuevamente
6. **Reset** - Marca todas las piezas como disponibles
7. **ARMAR rompecabezas** - Genera guia paso-a-paso desde pieza inicial
8. **Salir** - Cierra la aplicacion

### Ejemplo de Uso

```
Opcion: 2  # Aplicar schema
Opcion: 3  # Cargar puzzles
Opcion: 7  # Armar rompecabezas
Que pieza tienes? ID inicial (ej: ex_1): ex_1
```

Salida esperada:
```
=========================================================
  GUIA PARA ARMAR EL ROMPECABEZAS
=========================================================

  Paso 1: [INICIO] Toma la pieza #1
             (Pala/cuchara turquesa) -- colócala como base.

  Paso 2: [PIEZA] Toma la pieza #2
             (Brazo superior naranja con rueda negra)
             -> Tomala por: extremo superior de la pala
             -> Encájala en: extremo inferior del brazo de la pieza #1
...
=========================================================
```

## Estructura del Proyecto

```
rompecabezas-bd2/
├── src/
│   ├── db.py           # Conexion a Neo4j
│   ├── schema.py       # Constraints e indices
│   ├── loader.py       # Carga de puzzles desde JSON
│   ├── missing.py      # Gestion de piezas faltantes
│   ├── solver.py       # Algoritmo BFS de armado
│   └── main.py         # CLI principal
├── data/
│   └── puzzles/
│       ├── excavator.json    # Puzzle excavadora (completo)
│       ├── monsters.json     # Puzzle monstruos (completo)
│       ├── dolphins.json     # Plantilla delfines
│       └── city_grid.json    # Plantilla ciudad grid
├── tests/
│   └── test_solver.py  # Pruebas unitarias
├── requirements.txt    # Dependencias
├── .env.example        # Plantilla de credenciales
└── README.md           # Este archivo
```

## Puzzles Incluidos

### Excavator (Completo)
- 10 piezas
- 1 cluster
- Conexiones totalmente definidas
- ID prefijo: ex_

### Monsters (Completo)
- 13 piezas
- 3 clusters independientes
- Conexiones totalmente definidas
- ID prefijo: mo_

### Dolphins (Plantilla)
- 9 piezas
- 1 cluster
- Requiere confirmar conexiones reales
- ID prefijo: do_

### City Grid (Plantilla)
- 24 piezas (cuadricula 4x6)
- 1 cluster
- Requiere generar conexiones desde coordenadas
- ID prefijo: ci_

## Modelo de Datos

### Nodos

**Puzzle**
- `id`: identificador unico
- `nombre`: nombre del puzzle
- `tipo`: LIBRE | GRID | BANDEJA
- `marca`: marca comercial
- `material`: madera, foam, carton
- `tema`: tematica de la imagen
- `tiene_bandeja`: si requiere marco/base

**Cluster**
- `id`: identificador unico
- `puzzle_id`: puzzle al que pertenece
- `nombre_cluster`: nombre descriptivo
- `total_piezas`: numero de piezas

**Pieza**
- `id`: identificador unico
- `cluster_id`: cluster al que pertenece
- `numero_etiqueta`: numero escrito en la pieza (opcional)
- `descripcion_visual`: descripcion para el usuario
- `fila/columna`: coordenadas (solo para GRID)
- `disponible`: boolean (false si falta)

### Relaciones

**PERTENECE_A**: Cluster -> Puzzle, Pieza -> Cluster
**CONECTA_CON**: Pieza -> Pieza (bidireccional)
- Propiedades: descripcion_desde, descripcion_hacia, tipo_ensamble

## Algoritmo

El sistema usa BFS (Breadth-First Search) para recorrer el grafo:

1. Inicia desde una pieza proporcionada por el usuario
2. Explora todos los vecinos conectados
3. Para cada pieza:
   - Si esta disponible: genera instruccion de armado
   - Si falta: emite advertencia y continua igualmente
4. Genera lista ordenada de pasos
5. Reporta advertencias al final

Complejidad: O(V + E) donde V = piezas, E = conexiones

## Consultas Neo4j Utiles

Ver puzzle completo con estructura:
```cypher
MATCH (p:Puzzle {id:'puzzle_excavator'})<-[:PERTENECE_A]-(c:Cluster)<-[:PERTENECE_A]-(pz:Pieza)
RETURN p, c, pz;
```

Ver grafo de conexiones:
```cypher
MATCH (a:Pieza {cluster_id:'cluster_excavator_1'})-[r:CONECTA_CON]->(b:Pieza)
RETURN a, r, b;
```

Listar piezas faltantes:
```cypher
MATCH (p:Pieza {disponible:false})
RETURN p.id, p.numero_etiqueta, p.descripcion_visual;
```

Contar clusters por puzzle:
```cypher
MATCH (c:Cluster)-[:PERTENECE_A]->(p:Puzzle)
RETURN p.nombre, count(c) AS num_clusters;
```

## Ventajas de Neo4j vs SQL

| Aspecto | Neo4j | SQL |
|--------|-------|-----|
| Modelado grafo | Natural con relaciones | Tabla de adyacencia + JOINs |
| BFS desde pieza | Cypher nativo, rapido | CTEs recursivos, complejo |
| Multi-cluster | Estructura natural | Requiere logica adicional |
| Piezas faltantes | Solo marcar atributo | Igual pero traversal mas caro |
| Escalabilidad | Trivial | Consultas se ralentizan |

## Limitaciones

- **Dolphins.json**: requiere confirmar numero y disposicion real de las 9 piezas
- **City_grid.json**: requiere generar conexiones desde coordenadas reales
- Actualmente no soporta piezas con multiples orientaciones
- No valida que el rompecabezas sea realizable (asume conectividad valida)

## Testing

Ejecutar pruebas unitarias:
```bash
python -m pytest tests/
```

O con unittest:
```bash
python -m unittest discover tests
```

## Proximos Pasos

1. Completar archivos JSON de dolphins y city_grid con adyacencias reales
2. Agregar validacion de conectividad del grafo
3. Implementar visualizacion web del grafo
4. Agregar soporte para orientaciones de piezas (rotaciones)
5. Crear API REST para integrar con aplicaciones externas

## Autor

Proyecto de Base de Datos 2 - CC3089
Universidad del Valle de Guatemala, Semestre I 2026

## Licencia

Privada - Proyecto Academico
