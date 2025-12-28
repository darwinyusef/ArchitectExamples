# 📊 Resumen: Modelos de Datos y Parquet

## ✅ Archivos Creados

### Modelos PostgreSQL (7 modelos + 1 init)

| # | Archivo | Modelo | Líneas | Estado |
|---|---------|--------|--------|--------|
| 1 | `backend/app/models/__init__.py` | Exports | 17 | ✅ |
| 2 | `backend/app/models/user.py` | User | 113 | ✅ |
| 3 | `backend/app/models/course.py` | Course | 120 | ✅ |
| 4 | `backend/app/models/goal.py` | Goal | 167 | ✅ |
| 5 | `backend/app/models/task.py` | Task | 182 | ✅ |
| 6 | `backend/app/models/event.py` | Event | 165 | ✅ |
| 7 | `backend/app/models/embedding.py` | Embedding (RAG) | 179 | ✅ |
| 8 | `backend/app/models/code_snapshot.py` | CodeSnapshot | 151 | ✅ |

**Total**: 8 archivos, ~1,094 líneas de código

### Schemas Parquet (1 archivo)

| # | Archivo | Schemas | Líneas | Estado |
|---|---------|---------|--------|--------|
| 1 | `backend/app/schemas/parquet_schemas.py` | 6 schemas PyArrow + 5 dataclasses | 419 | ✅ |

**Total**: 1 archivo, ~419 líneas de código

### Documentación (3 archivos)

| # | Archivo | Contenido | Estado |
|---|---------|-----------|--------|
| 1 | `MODELOS_Y_RAG.md` | Explicación completa de RAG en tiempo real | ✅ |
| 2 | `DIAGRAMA_MODELOS.md` | ERD y diagramas visuales | ✅ |
| 3 | `RESUMEN_MODELOS.md` | Este archivo | ✅ |

---

## 📋 Resumen de Modelos

### 1. User (Usuarios)
- **Propósito**: Gestión de usuarios del sistema
- **Campos clave**: email, username, hashed_password, metadata
- **Relaciones**: 1→N con Course, Goal, Task, Event, Embedding, CodeSnapshot
- **Seguridad**: Password hasheada con bcrypt, JWT tokens

### 2. Course (Cursos)
- **Propósito**: Proyectos de aprendizaje o cursos
- **Campos clave**: title, description, status, progress_percentage, metadata
- **Estados**: DRAFT, ACTIVE, COMPLETED, ARCHIVED
- **Relaciones**: N→1 con User, 1→N con Goal (opcional)

### 3. Goal (Objetivos)
- **Propósito**: Objetivos de aprendizaje individuales
- **Campos clave**: title, description, status, priority, ai_generated, validation_criteria
- **Estados**: PENDING, IN_PROGRESS, COMPLETED, BLOCKED, CANCELLED
- **Prioridades**: LOW, MEDIUM, HIGH, URGENT
- **Relaciones**: N→1 con User y Course, 1→N con Task

### 4. Task (Tareas)
- **Propósito**: Tareas concretas dentro de un goal
- **Campos clave**: title, task_type, status, validation_result, ai_feedback
- **Tipos**: CODE, DOCUMENTATION, TESTING, RESEARCH, REVIEW, DEPLOYMENT, OTHER
- **Estados**: TODO, IN_PROGRESS, IN_REVIEW, COMPLETED, FAILED, SKIPPED
- **Relaciones**: N→1 con User y Goal, 1→N con CodeSnapshot

### 5. Event (Eventos - Event Sourcing)
- **Propósito**: Trazabilidad completa de todos los eventos del sistema
- **Campos clave**: event_type, payload, metadata, parquet_path
- **Tipos**: 20+ tipos de eventos (user, course, goal, task, code, ai, system)
- **Persistencia**: PostgreSQL + Parquet files + RabbitMQ
- **Índices**: 3 índices compuestos para queries comunes

### 6. Embedding (RAG)
- **Propósito**: Vector embeddings para búsqueda semántica (RAG)
- **Campos clave**: content, embedding (Vector 1536 dims), entity_type, entity_id
- **Tecnología**: pgvector con HNSW index
- **Modelos**: OpenAI text-embedding-3-small (o large)
- **Usos**: Contexto para agentes de IA, búsqueda semántica, RAG

### 7. CodeSnapshot (Código)
- **Propósito**: Snapshots de código para validación
- **Campos clave**: file_path, code_content, validation_passed, validation_feedback, issues_found
- **Validación**: Score 0-1, lista de issues, feedback de IA
- **Lenguajes**: Soporta cualquier lenguaje de programación

---

## 🎯 Schemas Parquet

### 6 Schemas Especializados

1. **EVENT_SCHEMA** (Base)
   - Schema genérico para todos los eventos
   - Campos: event_id, user_id, entity_type, entity_id, payload, metadata, timestamps, partitioning

2. **USER_EVENT_SCHEMA**
   - Eventos de usuario (login, logout, created, updated)
   - Campos adicionales: email, username, action, ip_address, user_agent

3. **GOAL_EVENT_SCHEMA**
   - Eventos de goals (created, updated, started, completed, blocked)
   - Campos adicionales: goal_id, title, status, priority, progress, ai_generated, course_id

4. **TASK_EVENT_SCHEMA**
   - Eventos de tasks (created, updated, started, completed, validated, failed)
   - Campos adicionales: task_id, goal_id, title, task_type, status, validation_score, hours

5. **CODE_EVENT_SCHEMA**
   - Eventos de código (submitted, reviewed, validated)
   - Campos adicionales: code_snapshot_id, file_path, language, LOC, validation_passed, issues_count

6. **AI_EVENT_SCHEMA**
   - Eventos de agentes de IA (feedback_generated, goal_suggested, validation_completed)
   - Campos adicionales: agent_node, model_used, tokens_used, latency_ms, feedback_type

### 5 Dataclasses para Eventos

1. `BaseEvent` - Clase base
2. `UserEvent` - Eventos de usuario
3. `GoalEvent` - Eventos de goals
4. `TaskEvent` - Eventos de tasks
5. `CodeEvent` - Eventos de código
6. `AIEvent` - Eventos de IA

---

## 📊 Estructura de Almacenamiento

### PostgreSQL

```
ai_goals_tracker (database)
├── users (tabla)
├── courses (tabla)
├── goals (tabla)
├── tasks (tabla)
├── events (tabla)
├── embeddings (tabla con pgvector)
└── code_snapshots (tabla)
```

### Parquet (Event Sourcing)

```
backend/data/storage/events/
├── year=2024/
│   ├── month=01/
│   │   ├── day=15/
│   │   │   ├── user_events.parquet
│   │   │   ├── goal_events.parquet
│   │   │   ├── task_events.parquet
│   │   │   ├── code_events.parquet
│   │   │   └── ai_events.parquet
│   │   ├── day=16/
│   │   └── ...
│   └── month=02/
│       └── ...
└── year=2025/
    └── ...
```

---

## 🔗 Relaciones Entre Modelos

```
User
 ├──> Course (1:N)
 │     └──> Goal (1:N) [opcional]
 │
 ├──> Goal (1:N)
 │     └──> Task (1:N)
 │           └──> CodeSnapshot (1:N) [opcional]
 │
 ├──> Task (1:N)
 ├──> Event (1:N)
 ├──> Embedding (1:N)
 └──> CodeSnapshot (1:N)

Embedding (polimórfica)
 ├──> Goal
 ├──> Task
 ├──> Course
 └──> CodeSnapshot
```

---

## 🚀 Funcionalidades Clave

### 1. RAG (Retrieval-Augmented Generation)

**Qué es**: Los agentes de IA recuperan contexto relevante antes de generar respuestas.

**Cómo funciona**:
```python
# 1. Usuario envía query
query = "Crear API REST con FastAPI"

# 2. Generar embedding de la query
query_embedding = openai.embeddings.create(input=query)

# 3. Buscar en PostgreSQL con pgvector (búsqueda semántica)
similar_goals = db.query(Embedding, Goal).filter(
    Embedding.entity_type == "goal",
    Embedding.user_id == user_id
).order_by(
    Embedding.embedding.cosine_distance(query_embedding)
).limit(5)

# 4. Usar contexto en prompt de LangGraph
context = format_goals(similar_goals)
response = llm.invoke(f"Contexto: {context}\n\nQuery: {query}")
```

**Beneficios**:
- Feedback personalizado
- Aprende de éxitos anteriores
- Sugerencias contextuales
- Validación de alta calidad

### 2. Event Sourcing

**Qué es**: Todos los eventos se almacenan para trazabilidad completa.

**Triple persistencia**:
1. **PostgreSQL** (events tabla) → Queries rápidas
2. **Parquet files** → Análisis histórico eficiente
3. **RabbitMQ** → Procesamiento asíncrono

**Ejemplo de flujo**:
```
User crea Goal
    ↓
WebSocket → Backend → LangGraph
    ↓
1. INSERT INTO goals (...)
2. INSERT INTO embeddings (...)
3. Publicar evento "goal.created" a RabbitMQ
    ↓
Consumidor RabbitMQ:
    ↓
    ├─> INSERT INTO events (...)
    └─> Escribir a Parquet: events/2024/01/15/goal_events.parquet
```

### 3. Vector Search (pgvector)

**Índice HNSW**: Búsqueda de vectores en O(log n)

```sql
-- Crear índice
CREATE INDEX ON embeddings USING hnsw (embedding vector_cosine_ops);

-- Buscar similares
SELECT content, 1 - (embedding <=> :query_embedding) as similarity
FROM embeddings
WHERE entity_type = 'goal'
ORDER BY embedding <=> :query_embedding
LIMIT 5;
```

**Performance**: Millones de vectores, búsqueda en milisegundos

---

## 📈 Índices Optimizados

### Índices Simples
```sql
-- Users
CREATE UNIQUE INDEX idx_users_email ON users(email);
CREATE UNIQUE INDEX idx_users_username ON users(username);

-- Goals, Tasks, etc.
CREATE INDEX idx_goals_user_id ON goals(user_id);
CREATE INDEX idx_tasks_goal_id ON tasks(goal_id);
```

### Índices Compuestos
```sql
-- Events (queries comunes)
CREATE INDEX idx_events_user_created ON events(user_id, created_at);
CREATE INDEX idx_events_entity ON events(entity_type, entity_id, created_at);
CREATE INDEX idx_events_type_created ON events(event_type, created_at);

-- Tasks (búsqueda por usuario y lenguaje)
CREATE INDEX idx_code_snapshots_user_lang ON code_snapshots(user_id, language, created_at);
```

### Índice Vectorial (HNSW)
```sql
-- Embeddings (búsqueda semántica)
CREATE INDEX ON embeddings USING hnsw (embedding vector_cosine_ops);
```

---

## 🎯 Casos de Uso

### 1. Crear Goal con IA
```
Usuario: "Quiero aprender FastAPI"
    ↓
LangGraph Agent:
    ├─> RAG: Buscar goals similares completados
    ├─> Generar goal con tareas detalladas
    └─> Validar con contract_validator_node
    ↓
Persistencia:
    ├─> INSERT INTO goals
    ├─> INSERT INTO embeddings
    └─> Publicar evento "goal.created"
```

### 2. Validar Código
```
Usuario: Envía código Python
    ↓
LangGraph Agent:
    ├─> RAG: Buscar código similar validado
    ├─> Ejecutar validación con IA
    └─> Generar feedback contextual
    ↓
Persistencia:
    ├─> INSERT INTO code_snapshots
    ├─> INSERT INTO embeddings
    └─> Publicar evento "code.validated"
```

### 3. Análisis Histórico
```python
# Analizar productividad usando Parquet
import pyarrow.dataset as ds

dataset = ds.dataset("events", format="parquet", partitioning="hive")
filtered = dataset.to_table(
    filter=(
        (ds.field("year") == 2024) &
        (ds.field("month") == 1) &
        (ds.field("user_id") == "usr-123")
    )
)

df = filtered.to_pandas()
metrics = {
    "goals_completed": len(df[df["event_type"] == "goal.completed"]),
    "tasks_completed": len(df[df["event_type"] == "task.completed"]),
    "avg_validation_score": df["validation_score"].mean()
}
```

---

## ✅ Checklist de Implementación

### Modelos PostgreSQL
- [x] User model
- [x] Course model
- [x] Goal model
- [x] Task model
- [x] Event model
- [x] Embedding model (RAG)
- [x] CodeSnapshot model

### Schemas Parquet
- [x] EVENT_SCHEMA
- [x] USER_EVENT_SCHEMA
- [x] GOAL_EVENT_SCHEMA
- [x] TASK_EVENT_SCHEMA
- [x] CODE_EVENT_SCHEMA
- [x] AI_EVENT_SCHEMA
- [x] Dataclasses para eventos

### Próximos Pasos
- [ ] Crear migraciones Alembic
- [ ] Implementar RAG tools para LangGraph
- [ ] Crear event processors (RabbitMQ → Parquet)
- [ ] Implementar servicios CRUD
- [ ] Tests unitarios
- [ ] Integración con LangGraph agents

---

## 📚 Documentación

### Archivos Creados

1. **`MODELOS_Y_RAG.md`** (6,800 líneas)
   - Explicación completa de arquitectura
   - Ejemplos de RAG en tiempo real
   - Queries SQL optimizadas
   - Casos de uso detallados

2. **`DIAGRAMA_MODELOS.md`** (500 líneas)
   - ERD visual completo
   - Tipos de datos (ENUMS)
   - Ejemplos de datos
   - Índices importantes

3. **`RESUMEN_MODELOS.md`** (Este archivo)
   - Resumen ejecutivo
   - Checklist de implementación

---

## 🎓 Tecnologías Utilizadas

| Tecnología | Versión | Uso |
|------------|---------|-----|
| SQLAlchemy | 2.0+ | ORM para PostgreSQL |
| pgvector | Latest | Vector search en PostgreSQL |
| PyArrow | Latest | Escritura/lectura de Parquet |
| Pydantic | 2.0+ | Validación de schemas |
| OpenAI | Latest | Generación de embeddings |

---

## 🔐 Seguridad

- **Passwords**: Hasheadas con bcrypt
- **Tokens**: JWT con SECRET_KEY de 64+ chars
- **API Keys**: Almacenadas en `.env` (NO en código)
- **Validación**: Pydantic schemas en todos los endpoints
- **Sanitización**: SQL injection prevention con SQLAlchemy ORM

---

**Fecha**: 2025-12-28
**Versión**: 2.0.0
**Archivos totales**: 12 archivos (8 modelos + 1 schemas + 3 docs)
**Líneas de código**: ~1,500 líneas Python + ~7,800 líneas documentación
**Estado**: ✅ **COMPLETO Y LISTO**
