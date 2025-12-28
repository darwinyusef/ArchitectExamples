# 📊 Diagrama de Modelos de Datos

## 🗄️ Esquema de Base de Datos (ERD)

```
┌──────────────────────────────────────────────────────────────────────────┐
│                           PostgreSQL Database                             │
│                        ai_goals_tracker (con pgvector)                   │
└──────────────────────────────────────────────────────────────────────────┘

┌─────────────────────┐
│      USERS          │
├─────────────────────┤
│ id (PK)            │──────┐
│ email (UNIQUE)     │      │
│ username (UNIQUE)  │      │
│ hashed_password    │      │
│ full_name          │      │
│ is_active          │      │
│ is_superuser       │      │
│ metadata (JSON)    │      │
│ created_at         │      │
│ updated_at         │      │
│ last_login_at      │      │
└─────────────────────┘      │
         │                   │
         │                   │
         ▼                   ▼
┌─────────────────────┐  ┌─────────────────────┐
│     COURSES         │  │       GOALS         │
├─────────────────────┤  ├─────────────────────┤
│ id (PK)            │  │ id (PK)            │
│ user_id (FK) ──────┼──┼─▶user_id (FK)      │──┐
│ title              │  │ course_id (FK) ────┤  │
│ description        │  │ title              │  │
│ status (ENUM)      │  │ description        │  │
│ progress_%         │  │ status (ENUM)      │  │
│ metadata (JSON)    │  │ priority (ENUM)    │  │
│ created_at         │  │ progress_%         │  │
│ updated_at         │  │ ai_generated       │  │
│ completed_at       │  │ validation_criteria│  │
└─────────────────────┘  │ metadata (JSON)    │  │
         │               │ created_at         │  │
         │               │ updated_at         │  │
         │               │ started_at         │  │
         │               │ completed_at       │  │
         │               │ due_date           │  │
         │               └─────────────────────┘  │
         │                        │               │
         │                        ▼               │
         │               ┌─────────────────────┐  │
         │               │       TASKS         │  │
         │               ├─────────────────────┤  │
         │               │ id (PK)            │  │
         │               │ goal_id (FK) ──────┘  │
         │               │ user_id (FK) ─────────┘
         │               │ title              │
         │               │ description        │
         │               │ task_type (ENUM)   │
         │               │ status (ENUM)      │
         │               │ priority (INT)     │
         │               │ estimated_hours    │
         │               │ actual_hours       │
         │               │ validation_result  │
         │               │ ai_feedback        │
         │               │ metadata (JSON)    │
         │               │ created_at         │
         │               │ updated_at         │
         │               │ started_at         │
         │               │ completed_at       │
         │               └─────────────────────┘
         │                        │
         │                        ▼
         │               ┌─────────────────────┐
         │               │  CODE_SNAPSHOTS     │
         │               ├─────────────────────┤
         │               │ id (PK)            │
         │               │ task_id (FK) ──────┘
         │               │ user_id (FK)       │
         │               │ file_path          │
         │               │ language           │
         │               │ code_content       │
         │               │ validation_passed  │
         │               │ validation_score   │
         │               │ validation_feedback│
         │               │ issues_found (JSON)│
         │               │ metadata (JSON)    │
         │               │ storage_path       │
         │               │ created_at         │
         │               └─────────────────────┘
         │
         ▼
┌─────────────────────┐      ┌─────────────────────┐
│      EVENTS         │      │    EMBEDDINGS       │
├─────────────────────┤      ├─────────────────────┤
│ id (PK)            │      │ id (PK)            │
│ event_type (ENUM)  │      │ user_id (FK)       │
│ user_id (FK)       │      │ entity_type        │
│ entity_type        │      │ entity_id          │
│ entity_id          │      │ content (TEXT)     │
│ payload (JSON)     │      │ embedding (VECTOR) │◀── pgvector
│ metadata (JSON)    │      │ model              │    (1536 dims)
│ created_at         │      │ metadata (JSON)    │
│ processed_at       │      │ created_at         │
│ parquet_path       │      └─────────────────────┘
└─────────────────────┘              │
         │                           │
         │                           ▼
         │                   [HNSW Index]
         │                   para búsqueda
         │                   semántica rápida
         │
         ▼
┌──────────────────────────────────────────┐
│        PARQUET FILES (Event Sourcing)    │
├──────────────────────────────────────────┤
│  events/                                 │
│  ├── year=2024/                          │
│  │   ├── month=01/                       │
│  │   │   ├── user_events.parquet        │
│  │   │   ├── goal_events.parquet        │
│  │   │   ├── task_events.parquet        │
│  │   │   ├── code_events.parquet        │
│  │   │   └── ai_events.parquet          │
│  │   └── month=02/                       │
│  │       └── ...                          │
│  └── year=2025/                          │
│      └── ...                              │
└──────────────────────────────────────────┘
```

---

## 📋 Tipos de Datos (ENUMS)

### CourseStatus
```python
DRAFT       # Borrador, no publicado
ACTIVE      # Curso activo
COMPLETED   # Curso completado
ARCHIVED    # Archivado
```

### GoalStatus
```python
PENDING      # Pendiente de iniciar
IN_PROGRESS  # En progreso
COMPLETED    # Completado
BLOCKED      # Bloqueado (dependencias)
CANCELLED    # Cancelado
```

### GoalPriority
```python
LOW      # Prioridad baja
MEDIUM   # Prioridad media
HIGH     # Prioridad alta
URGENT   # Urgente
```

### TaskStatus
```python
TODO        # Por hacer
IN_PROGRESS # En progreso
IN_REVIEW   # En revisión (IA)
COMPLETED   # Completada
FAILED      # Falló validación
SKIPPED     # Saltada
```

### TaskType
```python
CODE           # Tarea de código
DOCUMENTATION  # Tarea de documentación
TESTING        # Tarea de testing
RESEARCH       # Investigación
REVIEW         # Revisión de código
DEPLOYMENT     # Deployment
OTHER          # Otro tipo
```

### EventType (Event Sourcing)
```python
# User events
USER_CREATED, USER_UPDATED, USER_LOGIN, USER_LOGOUT

# Course events
COURSE_CREATED, COURSE_UPDATED, COURSE_COMPLETED, COURSE_ARCHIVED

# Goal events
GOAL_CREATED, GOAL_UPDATED, GOAL_STARTED, GOAL_COMPLETED, GOAL_BLOCKED

# Task events
TASK_CREATED, TASK_UPDATED, TASK_STARTED, TASK_COMPLETED,
TASK_VALIDATED, TASK_FAILED

# Code events
CODE_SUBMITTED, CODE_REVIEWED, CODE_VALIDATED

# AI events
AI_FEEDBACK_GENERATED, AI_GOAL_SUGGESTED, AI_VALIDATION_COMPLETED

# System events
SYSTEM_ERROR, SYSTEM_WARNING
```

---

## 🔗 Relaciones Entre Modelos

### 1. User → Courses (1:N)
Un usuario puede tener múltiples cursos.

```python
# En User model
courses: Mapped[List["Course"]] = relationship("Course", back_populates="owner")

# En Course model
owner: Mapped["User"] = relationship("User", back_populates="courses")
```

### 2. User → Goals (1:N)
Un usuario puede tener múltiples goals.

```python
# En User model
goals: Mapped[List["Goal"]] = relationship("Goal", back_populates="owner")

# En Goal model
owner: Mapped["User"] = relationship("User", back_populates="goals")
```

### 3. Course → Goals (1:N) [Opcional]
Un curso puede tener múltiples goals.

```python
# En Course model
goals: Mapped[List["Goal"]] = relationship("Goal", back_populates="course")

# En Goal model
course: Mapped[Optional["Course"]] = relationship("Course", back_populates="goals")
```

### 4. Goal → Tasks (1:N)
Un goal tiene múltiples tasks.

```python
# En Goal model
tasks: Mapped[List["Task"]] = relationship("Task", back_populates="goal")

# En Task model
goal: Mapped["Goal"] = relationship("Goal", back_populates="tasks")
```

### 5. Task → CodeSnapshots (1:N)
Una task puede tener múltiples snapshots de código.

```python
# En Task model
code_snapshots: Mapped[List["CodeSnapshot"]] = relationship("CodeSnapshot", back_populates="task")

# En CodeSnapshot model
task: Mapped[Optional["Task"]] = relationship("Task", back_populates="code_snapshots")
```

### 6. User → Embeddings (1:N)
Un usuario tiene múltiples embeddings (de sus goals, tasks, code).

```python
# En User model
embeddings: Mapped[List["Embedding"]] = relationship("Embedding", back_populates="user")

# En Embedding model
user: Mapped["User"] = relationship("User", back_populates="embeddings")
```

### 7. Embeddings → Entidades (Polimórfica)
Un embedding puede apuntar a cualquier entidad (goal, task, course, code_snapshot).

```python
# En Embedding model
entity_type: str  # "goal", "task", "course", "code_snapshot"
entity_id: str    # ID de la entidad

# Query para obtener embeddings de un goal:
embeddings = session.query(Embedding).filter(
    Embedding.entity_type == "goal",
    Embedding.entity_id == goal_id
).all()
```

---

## 🎯 Ejemplos de Datos

### User
```json
{
  "id": "usr_abc123",
  "email": "dev@example.com",
  "username": "developer",
  "full_name": "Juan Developer",
  "is_active": true,
  "metadata": {
    "preferences": {"theme": "dark", "language": "es"},
    "profile": {"avatar_url": "https://...", "bio": "Full-stack developer"}
  },
  "created_at": "2024-01-15T10:00:00Z"
}
```

### Course
```json
{
  "id": "crs_xyz789",
  "user_id": "usr_abc123",
  "title": "FastAPI Master Course",
  "description": "Aprende FastAPI desde cero",
  "status": "active",
  "progress_percentage": 45.5,
  "metadata": {
    "technologies": ["Python", "FastAPI", "PostgreSQL"],
    "difficulty": "intermediate",
    "estimated_hours": 40
  }
}
```

### Goal
```json
{
  "id": "gol_def456",
  "user_id": "usr_abc123",
  "course_id": "crs_xyz789",
  "title": "Crear API REST con autenticación JWT",
  "description": "Implementar un sistema completo de auth",
  "status": "in_progress",
  "priority": "high",
  "progress_percentage": 60.0,
  "ai_generated": true,
  "validation_criteria": {
    "criteria": [
      "Implementar login y registro",
      "Generar tokens JWT",
      "Validar tokens en endpoints protegidos"
    ]
  }
}
```

### Task
```json
{
  "id": "tsk_ghi789",
  "goal_id": "gol_def456",
  "user_id": "usr_abc123",
  "title": "Implementar endpoint /login",
  "task_type": "code",
  "status": "completed",
  "validation_result": {
    "passed": true,
    "score": 0.95,
    "issues": [],
    "validated_at": "2024-01-16T14:30:00Z"
  },
  "ai_feedback": "¡Excelente trabajo! Tu implementación es segura y sigue las mejores prácticas."
}
```

### CodeSnapshot
```json
{
  "id": "cs_jkl012",
  "task_id": "tsk_ghi789",
  "user_id": "usr_abc123",
  "file_path": "/api/auth/login.py",
  "language": "python",
  "code_content": "async def login(...): ...",
  "validation_passed": true,
  "validation_score": 0.95,
  "issues_found": [],
  "metadata": {
    "lines_of_code": 45,
    "complexity": "low",
    "test_coverage": 0.92
  }
}
```

### Event
```json
{
  "id": "evt_mno345",
  "event_type": "task.completed",
  "user_id": "usr_abc123",
  "entity_type": "task",
  "entity_id": "tsk_ghi789",
  "payload": {
    "task_id": "tsk_ghi789",
    "title": "Implementar endpoint /login",
    "validation_score": 0.95
  },
  "metadata": {
    "ip_address": "192.168.1.1",
    "source": "vscode_extension"
  },
  "created_at": "2024-01-16T14:30:00Z"
}
```

### Embedding
```json
{
  "id": "emb_pqr678",
  "user_id": "usr_abc123",
  "entity_type": "goal",
  "entity_id": "gol_def456",
  "content": "Crear API REST con autenticación JWT. Implementar un sistema completo de auth...",
  "embedding": [0.123, -0.456, 0.789, ...],  // 1536 dimensiones
  "model": "text-embedding-3-small",
  "created_at": "2024-01-15T10:05:00Z"
}
```

---

## 📊 Cardinalidad

```
User (1) ──────── (N) Course
User (1) ──────── (N) Goal
User (1) ──────── (N) Task
User (1) ──────── (N) Event
User (1) ──────── (N) Embedding
User (1) ──────── (N) CodeSnapshot

Course (1) ──────── (N) Goal [Opcional]

Goal (1) ──────── (N) Task

Task (1) ──────── (N) CodeSnapshot [Opcional]

Embedding (*) ──────── (1) Entity [Polimórfica]
  - entity_type + entity_id apuntan a Goal, Task, Course o CodeSnapshot
```

---

## 🔍 Índices Importantes

### Para Queries Rápidas

```sql
-- Users
CREATE UNIQUE INDEX idx_users_email ON users(email);
CREATE UNIQUE INDEX idx_users_username ON users(username);

-- Goals
CREATE INDEX idx_goals_user_id ON goals(user_id);
CREATE INDEX idx_goals_status ON goals(status, created_at);
CREATE INDEX idx_goals_course_id ON goals(course_id);

-- Tasks
CREATE INDEX idx_tasks_goal_id ON tasks(goal_id);
CREATE INDEX idx_tasks_status ON tasks(status, created_at);
CREATE INDEX idx_tasks_user_id ON tasks(user_id);

-- Events (compuestos)
CREATE INDEX idx_events_user_created ON events(user_id, created_at);
CREATE INDEX idx_events_entity ON events(entity_type, entity_id, created_at);
CREATE INDEX idx_events_type_created ON events(event_type, created_at);

-- Embeddings
CREATE INDEX idx_embeddings_entity ON embeddings(entity_type, entity_id);
CREATE INDEX ON embeddings USING hnsw (embedding vector_cosine_ops);

-- CodeSnapshots
CREATE INDEX idx_code_snapshots_validated ON code_snapshots(validation_passed, created_at);
CREATE INDEX idx_code_snapshots_language ON code_snapshots(user_id, language);
```

---

## 🚀 Migración con Alembic

Estructura de migraciones:

```
backend/alembic/versions/
├── 001_create_users_table.py
├── 002_create_courses_table.py
├── 003_create_goals_table.py
├── 004_create_tasks_table.py
├── 005_create_code_snapshots_table.py
├── 006_create_events_table.py
├── 007_create_embeddings_table.py
└── 008_create_indexes.py
```

---

**Versión**: 2.0.0
**Fecha**: 2025-12-28
**Total Modelos**: 7 tablas PostgreSQL + 6 schemas Parquet
