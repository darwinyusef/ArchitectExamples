# 🗄️ Modelos de Datos y RAG en Tiempo Real

## 📊 Resumen de Modelos Creados

### Modelos PostgreSQL (7 tablas)

| Modelo | Archivo | Propósito |
|--------|---------|-----------|
| `User` | `models/user.py` | Usuarios del sistema |
| `Course` | `models/course.py` | Cursos/proyectos de aprendizaje |
| `Goal` | `models/goal.py` | Objetivos de aprendizaje |
| `Task` | `models/task.py` | Tareas individuales |
| `Event` | `models/event.py` | Event Sourcing (todos los eventos) |
| `Embedding` | `models/embedding.py` | Vectores para RAG |
| `CodeSnapshot` | `models/code_snapshot.py` | Código para validación |

### Schemas Parquet (6 schemas)

| Schema | Propósito |
|--------|-----------|
| `EVENT_SCHEMA` | Schema base para todos los eventos |
| `USER_EVENT_SCHEMA` | Eventos de usuario |
| `GOAL_EVENT_SCHEMA` | Eventos de goals |
| `TASK_EVENT_SCHEMA` | Eventos de tasks |
| `CODE_EVENT_SCHEMA` | Eventos de validación de código |
| `AI_EVENT_SCHEMA` | Eventos de agentes de IA |

---

## 🎯 Arquitectura de Persistencia en Tiempo Real

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (VS Code)                        │
│                  WebSocket Connection                        │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  BACKEND (FastAPI)                           │
│                                                              │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐  │
│  │  WebSocket  │────▶│  LangGraph  │────▶│   Storage   │  │
│  │   Handler   │     │   Agents    │     │   Service   │  │
│  └─────────────┘     └─────────────┘     └─────────────┘  │
│         │                   │                    │          │
│         │                   │                    │          │
│         ▼                   ▼                    ▼          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              EVENT PUBLISHING                         │  │
│  │        (RabbitMQ + Event Processors)                 │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────┬───────────────────┬─────────────────────┘
                   │                   │
                   ▼                   ▼
    ┌──────────────────────┐   ┌──────────────────────┐
    │    PostgreSQL        │   │   Parquet Files      │
    │  (Queries rápidas)   │   │ (Análisis histórico) │
    │                      │   │                      │
    │  ┌────────────────┐  │   │  ┌────────────────┐ │
    │  │ Embeddings     │  │   │  │ Events/        │ │
    │  │ (pgvector)     │  │   │  │  2024/01/...   │ │
    │  │                │  │   │  │  2024/02/...   │ │
    │  │ RAG Search ────┼──┼───┼─▶│                │ │
    │  └────────────────┘  │   │  └────────────────┘ │
    └──────────────────────┘   └──────────────────────┘
```

---

## 🔄 Flujo de Datos en Tiempo Real

### 1. Usuario Crea un Goal (Ejemplo)

```
┌─────────────────────────────────────────────────────────────┐
│ PASO 1: Usuario hace click en "Create Goal" en VS Code     │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ PASO 2: WebSocket envía mensaje al backend                  │
│                                                              │
│ {                                                            │
│   "type": "goal.create",                                    │
│   "payload": {                                              │
│     "title": "Aprender FastAPI",                           │
│     "description": "Crear una API REST completa"           │
│   }                                                         │
│ }                                                           │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ PASO 3: LangGraph Agent (goal_generator_node)               │
│                                                              │
│ 1. Recibe request                                           │
│ 2. Busca contexto en RAG:                                   │
│    - Goals similares anteriores                             │
│    - Documentación de cursos relacionados                   │
│    - Código de referencia validado                          │
│ 3. Genera goal completo con IA                             │
│ 4. Valida con contract_validator_node                      │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ PASO 4: Persistencia TRIPLE                                 │
│                                                              │
│ A) PostgreSQL (inmediato):                                  │
│    INSERT INTO goals (...) VALUES (...)                     │
│                                                              │
│ B) Embedding (inmediato):                                   │
│    - Generar embedding del goal                             │
│    - INSERT INTO embeddings (...) VALUES (...)             │
│                                                              │
│ C) Event Sourcing:                                          │
│    - Publicar a RabbitMQ: "goal.created"                   │
│    - Consumidor guarda en PostgreSQL events table          │
│    - Consumidor guarda en Parquet file                     │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ PASO 5: Respuesta en tiempo real vía WebSocket             │
│                                                              │
│ Frontend recibe:                                            │
│ {                                                           │
│   "type": "goal.created",                                  │
│   "payload": {                                             │
│     "goal_id": "123",                                      │
│     "title": "Aprender FastAPI",                          │
│     "tasks": [...],  // IA generó tareas automáticamente  │
│     "ai_feedback": "..."                                   │
│   }                                                        │
│ }                                                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 🤖 RAG (Retrieval-Augmented Generation) en Acción

### ¿Qué es RAG?

RAG permite a los agentes de IA **recuperar contexto relevante** antes de generar respuestas.

### Ejemplo: Agente de Feedback (Nodo 4)

Cuando el usuario pide feedback sobre su código:

```python
# 1. Usuario envía código
code = """
async def get_user(user_id: str):
    user = db.query(User).filter(User.id == user_id).first()
    return user
"""

# 2. Agente genera embedding del código
from openai import OpenAI
client = OpenAI()

code_embedding = client.embeddings.create(
    model="text-embedding-3-small",
    input=code
).data[0].embedding

# 3. Buscar código similar en la base de datos (RAG)
query = """
SELECT cs.code_content, cs.validation_feedback,
       1 - (e.embedding <=> :query_embedding) as similarity
FROM embeddings e
JOIN code_snapshots cs ON e.entity_id = cs.id
WHERE e.entity_type = 'code_snapshot'
  AND cs.language = 'python'
  AND cs.validation_passed = true
ORDER BY e.embedding <=> :query_embedding
LIMIT 5;
"""

# Resultado: 5 ejemplos de código similar que YA FUE VALIDADO
similar_code = [
    {
        "code": "async def get_user_by_id(id: str, db: Session): ...",
        "feedback": "Bien hecho! Usa dependency injection correctamente",
        "similarity": 0.92
    },
    # ... más ejemplos
]

# 4. Agente usa el contexto recuperado para generar feedback
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

llm = ChatOpenAI(model="gpt-4o-mini")

prompt = ChatPromptTemplate.from_messages([
    ("system", """Eres un experto en FastAPI.

Revisa el código del usuario y proporciona feedback.

Contexto de código similar validado:
{context}
"""),
    ("user", "Revisa este código:\n{code}")
])

# El contexto de RAG mejora la calidad del feedback
chain = prompt | llm
feedback = chain.invoke({
    "code": code,
    "context": format_similar_code(similar_code)
})

# 5. Feedback contextualizado y de alta calidad
print(feedback.content)
# "Tu código es correcto, pero te falta dependency injection.
#  Mira este ejemplo validado que es similar:
#
#  async def get_user_by_id(id: str, db: Session = Depends(get_db)):
#      return db.query(User).filter(User.id == id).first()
#
#  Nota la diferencia: usamos Depends() para inyectar la sesión DB."
```

---

## 📈 Consultas RAG Optimizadas

### 1. Buscar Goals Similares (para Agente de Goals)

```sql
-- Encuentra goals similares para sugerir tareas
SELECT
    g.id,
    g.title,
    g.description,
    e.content,
    1 - (e.embedding <=> :query_embedding) as similarity
FROM embeddings e
JOIN goals g ON e.entity_id = g.id
WHERE
    e.entity_type = 'goal'
    AND e.user_id = :user_id
    AND g.status = 'completed'  -- Solo goals completados (aprendemos de éxitos)
ORDER BY e.embedding <=> :query_embedding
LIMIT 5;
```

### 2. Buscar Documentación de Cursos (para Agente de Cursos)

```sql
-- Encuentra documentación relevante de cursos
SELECT
    c.id,
    c.title,
    e.content,
    c.metadata->>'technologies' as technologies,
    1 - (e.embedding <=> :query_embedding) as similarity
FROM embeddings e
JOIN courses c ON e.entity_id = c.id
WHERE
    e.entity_type = 'course'
    AND e.user_id = :user_id
ORDER BY e.embedding <=> :query_embedding
LIMIT 3;
```

### 3. Buscar Código Validado (para Agente de Validación)

```sql
-- Encuentra código similar ya validado
SELECT
    cs.id,
    cs.file_path,
    cs.code_content,
    cs.validation_feedback,
    cs.validation_score,
    e.content,
    1 - (e.embedding <=> :query_embedding) as similarity
FROM embeddings e
JOIN code_snapshots cs ON e.entity_id = cs.id
WHERE
    e.entity_type = 'code_snapshot'
    AND cs.language = :language
    AND cs.validation_passed = true
    AND cs.validation_score > 0.8  -- Solo código de alta calidad
ORDER BY e.embedding <=> :query_embedding
LIMIT 5;
```

---

## 🔍 Índices para Performance

Los modelos incluyen índices optimizados:

### PostgreSQL Indexes

```sql
-- Embeddings: HNSW index para búsqueda de vectores
CREATE INDEX ON embeddings USING hnsw (embedding vector_cosine_ops);

-- Events: Índices compuestos para queries comunes
CREATE INDEX idx_events_user_created ON events(user_id, created_at);
CREATE INDEX idx_events_entity ON events(entity_type, entity_id, created_at);
CREATE INDEX idx_events_type_created ON events(event_type, created_at);

-- Tasks: Búsqueda por validación
CREATE INDEX idx_code_snapshots_validated ON code_snapshots(validation_passed, created_at);

-- Goals: Búsqueda por estado
CREATE INDEX ON goals(status, created_at);
```

### Parquet Partitioning

```
events/
├── year=2024/
│   ├── month=01/
│   │   ├── day=15/
│   │   │   ├── goal_events.parquet
│   │   │   ├── task_events.parquet
│   │   │   └── code_events.parquet
│   │   └── day=16/
│   └── month=02/
```

Permite queries rápidas como:

```python
import pyarrow.dataset as ds

# Solo leer eventos de enero 2024
dataset = ds.dataset("events", format="parquet", partitioning="hive")
filtered = dataset.to_table(
    filter=(ds.field("year") == 2024) & (ds.field("month") == 1)
)
```

---

## 🚀 Ejemplo Completo: Agente con RAG

```python
# backend/app/agents/tools/rag_tools.py

from typing import List, Dict
from sqlalchemy import text
from app.core.database import AsyncSessionLocal
from openai import AsyncOpenAI

async def get_similar_goals(
    query: str,
    user_id: str,
    limit: int = 5
) -> List[Dict]:
    """
    Recuperar goals similares usando RAG.

    Args:
        query: Texto para buscar (ej: descripción del nuevo goal)
        user_id: ID del usuario
        limit: Número de resultados

    Returns:
        Lista de goals similares con similarity score
    """
    # 1. Generar embedding de la query
    client = AsyncOpenAI()
    response = await client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    )
    query_embedding = response.data[0].embedding

    # 2. Buscar en PostgreSQL con pgvector
    async with AsyncSessionLocal() as db:
        sql = text("""
            SELECT
                g.id,
                g.title,
                g.description,
                g.status,
                g.progress_percentage,
                e.content,
                1 - (e.embedding <=> :embedding) as similarity
            FROM embeddings e
            JOIN goals g ON e.entity_id = g.id
            WHERE
                e.entity_type = 'goal'
                AND e.user_id = :user_id
                AND g.status = 'completed'
            ORDER BY e.embedding <=> :embedding
            LIMIT :limit
        """)

        result = await db.execute(
            sql,
            {
                "embedding": str(query_embedding),
                "user_id": user_id,
                "limit": limit
            }
        )

        rows = result.fetchall()

        return [
            {
                "goal_id": row[0],
                "title": row[1],
                "description": row[2],
                "status": row[3],
                "progress": row[4],
                "content": row[5],
                "similarity": row[6]
            }
            for row in rows
        ]


# Uso en agente LangGraph
from langgraph.graph import StateGraph
from langchain_openai import ChatOpenAI

async def goal_generator_node(state: AgentState):
    """Nodo que genera goals usando RAG."""

    user_input = state["messages"][-1].content
    user_id = state["user_id"]

    # 1. Recuperar contexto con RAG
    similar_goals = await get_similar_goals(
        query=user_input,
        user_id=user_id,
        limit=5
    )

    # 2. Formatear contexto
    context = "\n\n".join([
        f"Goal similar (score: {g['similarity']:.2f}):\n"
        f"  Título: {g['title']}\n"
        f"  Descripción: {g['description']}\n"
        f"  Progreso final: {g['progress']}%"
        for g in similar_goals
    ])

    # 3. Generar con LLM usando contexto
    llm = ChatOpenAI(model="gpt-4o-mini")

    prompt = f"""Eres un asistente experto en crear objetivos de aprendizaje.

El usuario quiere: {user_input}

Contexto de goals similares que ya completó:
{context}

Genera un goal detallado con:
1. Título claro
2. Descripción específica
3. Lista de 3-5 tareas concretas
4. Criterios de validación

Formato JSON:
{{
    "title": "...",
    "description": "...",
    "tasks": [...],
    "validation_criteria": [...]
}}
"""

    response = await llm.ainvoke(prompt)

    # 4. Guardar goal Y su embedding para futuro RAG
    goal_data = parse_json(response.content)

    # Guardar en DB...
    # Generar embedding del goal...
    # Publicar evento...

    return state
```

---

## 📊 Análisis Histórico con Parquet

```python
# backend/app/services/analytics.py

import pyarrow.parquet as pq
import pyarrow.dataset as ds
import pandas as pd
from datetime import datetime, timedelta

def analyze_user_productivity(user_id: str, days: int = 30):
    """
    Analizar productividad del usuario usando eventos Parquet.

    Args:
        user_id: ID del usuario
        days: Días hacia atrás para analizar

    Returns:
        Diccionario con métricas de productividad
    """
    # 1. Cargar dataset particionado
    dataset = ds.dataset(
        "backend/data/storage/events",
        format="parquet",
        partitioning="hive"
    )

    # 2. Filtrar por usuario y fecha
    start_date = datetime.now() - timedelta(days=days)

    table = dataset.to_table(
        filter=(
            (ds.field("user_id") == user_id) &
            (ds.field("created_at") >= start_date)
        )
    )

    # 3. Convertir a Pandas para análisis
    df = table.to_pandas()

    # 4. Análisis
    metrics = {
        "total_events": len(df),
        "goals_created": len(df[df["event_type"] == "goal.created"]),
        "goals_completed": len(df[df["event_type"] == "goal.completed"]),
        "tasks_completed": len(df[df["event_type"] == "task.completed"]),
        "code_validated": len(df[df["event_type"] == "code.validated"]),
        "avg_validation_score": df[
            df["event_type"] == "code.validated"
        ]["validation_score"].mean(),
        "most_active_day": df.groupby(df["created_at"].dt.day_name()).size().idxmax(),
        "events_by_type": df["event_type"].value_counts().to_dict()
    }

    return metrics


# Uso
metrics = analyze_user_productivity("user-123", days=30)
print(f"Productividad de usuario-123 (últimos 30 días):")
print(f"  - Goals completados: {metrics['goals_completed']}")
print(f"  - Tasks completadas: {metrics['tasks_completed']}")
print(f"  - Score promedio validación: {metrics['avg_validation_score']:.2f}")
```

---

## ✅ Beneficios de esta Arquitectura

### 1. **RAG en Tiempo Real**
- Los agentes siempre tienen contexto relevante
- Aprenden de éxitos anteriores del usuario
- Feedback personalizado y de alta calidad

### 2. **Triple Persistencia**
- PostgreSQL: Queries rápidas en tiempo real
- Embeddings (pgvector): Búsqueda semántica
- Parquet: Análisis histórico eficiente

### 3. **Event Sourcing**
- Trazabilidad completa
- Reproducibilidad de estados
- Auditoría total

### 4. **Performance Optimizado**
- Índices HNSW para búsqueda de vectores (O(log n))
- Particionamiento de Parquet por fecha
- Índices compuestos en PostgreSQL

### 5. **Escalabilidad**
- Parquet escala a terabytes
- RabbitMQ maneja millones de eventos/día
- pgvector escala a millones de vectores

---

## 🔗 Relación con Frontend

El frontend en `/proyectos/pixel-verse-academy` puede:

1. **Consultar goals/tasks** vía API REST
2. **Recibir actualizaciones en tiempo real** vía WebSocket
3. **Mostrar feedback de IA** con contexto RAG
4. **Visualizar progreso** basado en eventos históricos

---

## 📚 Próximos Pasos

1. ✅ Modelos creados
2. ✅ Schemas Parquet definidos
3. ⏳ Crear migraciones Alembic
4. ⏳ Implementar RAG tools para agentes
5. ⏳ Crear event processors (RabbitMQ → Parquet)
6. ⏳ Implementar analytics endpoints

---

**Versión**: 2.0.0
**Fecha**: 2025-12-28
**Estado**: ✅ Modelos y schemas completos
