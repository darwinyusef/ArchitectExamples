# 🗄️ Migraciones de Base de Datos - Alembic

## ✅ Archivos Creados

### Configuración Alembic (4 archivos)
1. **`alembic.ini`** - Configuración principal de Alembic
2. **`alembic/env.py`** - Environment setup, importa modelos
3. **`alembic/script.py.mako`** - Template para nuevas migraciones
4. **`alembic/README`** - Comandos rápidos de referencia

### Migraciones (7 archivos)
1. **`001_create_users_table.py`** - ⚠️ Temporal (vive en /proyectos/aquicreamos_2025/aqc/app)
2. **`002_create_courses_table.py`** - ⚠️ Temporal (vive en /proyectos/aquicreamos_2025/aqc/app)
3. **`003_create_goals_table.py`** - ✅ Core (este microservicio)
4. **`004_create_tasks_table.py`** - ✅ Core (este microservicio)
5. **`005_create_code_snapshots_table.py`** - ✅ Core (este microservicio)
6. **`006_create_events_table.py`** - ✅ Core (este microservicio)
7. **`007_create_embeddings_table.py`** - ✅ Core (este microservicio) + pgvector

### Scripts (1 archivo)
8. **`migrate.sh`** - Script automatizado para ejecutar migraciones

---

## 🚀 Uso Rápido

### 1. Setup Inicial

```bash
# Verificar que PostgreSQL está corriendo
psql -U YOUR_DB_USER -c "SELECT version();"

# Crear base de datos
createdb -U YOUR_DB_USER ai_goals_tracker

# Habilitar extensión pgvector
psql -U YOUR_DB_USER -d ai_goals_tracker -c "CREATE EXTENSION vector;"
```

### 2. Ejecutar Migraciones

```bash
cd backend

# Aplicar todas las migraciones
./migrate.sh upgrade

# Ver estado actual
./migrate.sh current

# Ver historial
./migrate.sh history
```

---

## 📋 Comandos Disponibles

### Script Automatizado (Recomendado)

```bash
./migrate.sh upgrade       # Aplicar todas las migraciones
./migrate.sh downgrade     # Revertir última migración
./migrate.sh current       # Ver revisión actual
./migrate.sh history       # Ver historial completo
./migrate.sh create "msg"  # Crear nueva migración
./migrate.sh reset         # PELIGRO: Reiniciar DB completa
./migrate.sh help          # Mostrar ayuda
```

### Comandos Alembic Directos

```bash
# Aplicar migraciones
poetry run alembic upgrade head

# Revertir una migración
poetry run alembic downgrade -1

# Ver estado actual
poetry run alembic current

# Ver historial
poetry run alembic history

# Crear nueva migración (autogenerate)
poetry run alembic revision --autogenerate -m "descripción"

# Crear migración vacía
poetry run alembic revision -m "descripción"

# Ir a revisión específica
poetry run alembic upgrade <revision_id>
```

---

## 🗄️ Tablas Creadas

### 1. Users (Temporal - ⚠️)
**Nota**: Esta tabla es temporal. Los users realmente viven en `/proyectos/aquicreamos_2025/aqc/app`.

```sql
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    metadata JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP
);
```

### 2. Courses (Temporal - ⚠️)
**Nota**: Esta tabla es temporal. Los courses realmente viven en `/proyectos/aquicreamos_2025/aqc/app`.

```sql
CREATE TABLE courses (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    status coursestatus NOT NULL DEFAULT 'draft',
    progress_percentage FLOAT NOT NULL DEFAULT 0.0,
    metadata JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);
```

### 3. Goals ✅
**Core de este microservicio**

```sql
CREATE TABLE goals (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) REFERENCES users(id) ON DELETE CASCADE,
    course_id VARCHAR(36) REFERENCES courses(id) ON DELETE SET NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    status goalstatus NOT NULL DEFAULT 'pending',
    priority goalpriority NOT NULL DEFAULT 'medium',
    progress_percentage FLOAT NOT NULL DEFAULT 0.0,
    ai_generated BOOLEAN NOT NULL DEFAULT FALSE,
    validation_criteria JSONB,
    metadata JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    due_date TIMESTAMP
);
```

### 4. Tasks ✅
**Core de este microservicio**

```sql
CREATE TABLE tasks (
    id VARCHAR(36) PRIMARY KEY,
    goal_id VARCHAR(36) REFERENCES goals(id) ON DELETE CASCADE,
    user_id VARCHAR(36) REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    task_type tasktype NOT NULL DEFAULT 'code',
    status taskstatus NOT NULL DEFAULT 'todo',
    priority INTEGER NOT NULL DEFAULT 100,
    estimated_hours FLOAT,
    actual_hours FLOAT,
    validation_result JSONB,
    ai_feedback TEXT,
    metadata JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);
```

### 5. Code Snapshots ✅
**Core de este microservicio**

```sql
CREATE TABLE code_snapshots (
    id VARCHAR(36) PRIMARY KEY,
    task_id VARCHAR(36) REFERENCES tasks(id) ON DELETE CASCADE,
    user_id VARCHAR(36) REFERENCES users(id) ON DELETE CASCADE,
    file_path VARCHAR(1000) NOT NULL,
    language VARCHAR(50) NOT NULL,
    code_content TEXT NOT NULL,
    validation_passed BOOLEAN,
    validation_score FLOAT,
    validation_feedback TEXT,
    issues_found JSONB,
    metadata JSONB,
    storage_path VARCHAR(500),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### 6. Events ✅
**Core de este microservicio - Event Sourcing**

```sql
CREATE TABLE events (
    id VARCHAR(36) PRIMARY KEY,
    event_type eventtype NOT NULL,
    user_id VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL,
    entity_type VARCHAR(50),
    entity_id VARCHAR(36),
    payload JSONB NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    parquet_path VARCHAR(500)
);
```

### 7. Embeddings ✅
**Core de este microservicio - RAG con pgvector**

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE embeddings (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) REFERENCES users(id) ON DELETE CASCADE,
    entity_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(36) NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536) NOT NULL,  -- pgvector!
    model VARCHAR(100) NOT NULL DEFAULT 'text-embedding-3-small',
    metadata JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- HNSW index para búsqueda vectorial ultra-rápida
CREATE INDEX idx_embeddings_vector_hnsw
ON embeddings USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

---

## 🎯 Índices Creados

### Users
- `idx_users_email` (email)
- `idx_users_username` (username)
- `idx_users_is_active` (is_active)

### Courses
- `idx_courses_user_id` (user_id)
- `idx_courses_status` (status, created_at)

### Goals
- `idx_goals_user_id` (user_id)
- `idx_goals_course_id` (course_id)
- `idx_goals_status` (status, created_at)
- `idx_goals_priority` (priority, created_at)

### Tasks
- `idx_tasks_goal_id` (goal_id)
- `idx_tasks_user_id` (user_id)
- `idx_tasks_status` (status, created_at)
- `idx_tasks_type` (task_type, created_at)

### Code Snapshots
- `idx_code_snapshots_task_id` (task_id, created_at)
- `idx_code_snapshots_user_id` (user_id)
- `idx_code_snapshots_language` (language, created_at)
- `idx_code_snapshots_validated` (validation_passed, created_at)
- `idx_code_snapshots_user_lang` (user_id, language, created_at)

### Events
- `idx_events_user_created` (user_id, created_at)
- `idx_events_entity` (entity_type, entity_id, created_at)
- `idx_events_type_created` (event_type, created_at)
- `idx_events_created_at` (created_at)

### Embeddings
- `idx_embeddings_user_id` (user_id)
- `idx_embeddings_entity` (entity_type, entity_id)
- `idx_embeddings_created_at` (created_at)
- **`idx_embeddings_vector_hnsw`** (embedding) - HNSW para búsqueda vectorial

---

## ⚠️ Integración con Microservicio de Users

### Estado Actual (Desarrollo)
Las tablas `users` y `courses` están presentes temporalmente para facilitar el desarrollo standalone.

### Estado Futuro (Producción)
- **Users y Courses** vivirán en `/proyectos/aquicreamos_2025/aqc/app`
- `user_id` y `course_id` en goals/tasks serán **referencias externas** (NO foreign keys)
- Autenticación vía JWT compartido entre servicios
- Consultas a users/courses vía REST API al otro microservicio

### Migración Futura

Cuando se integre con el otro microservicio:

1. **Modificar migración 003** (goals):
```python
# Cambiar de:
sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'))
sa.Column('course_id', sa.String(36), sa.ForeignKey('courses.id', ondelete='SET NULL'))

# A:
sa.Column('user_id', sa.String(36), nullable=False, index=True)
sa.Column('course_id', sa.String(36), nullable=True, index=True)
```

2. **Modificar migración 004** (tasks):
```python
# Cambiar de:
sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'))

# A:
sa.Column('user_id', sa.String(36), nullable=False, index=True)
```

3. **Eliminar migraciones** 001 y 002 (users y courses)

---

## 🔧 Troubleshooting

### Error: "relation already exists"

```bash
# Opción 1: Drop manual y recrear
psql -U YOUR_DB_USER -d ai_goals_tracker -c "DROP TABLE IF EXISTS users CASCADE;"
./migrate.sh upgrade

# Opción 2: Reset completo
./migrate.sh reset
```

### Error: "extension vector does not exist"

```bash
# Habilitar pgvector
psql -U YOUR_DB_USER -d ai_goals_tracker -c "CREATE EXTENSION vector;"

# Luego ejecutar migración
./migrate.sh upgrade
```

### Error: "could not connect to database"

```bash
# Verificar que PostgreSQL está corriendo
pg_isready -U YOUR_DB_USER

# Verificar DATABASE_URL en .env
cat ../.env | grep DATABASE_URL
```

### Ver queries SQL generadas

```bash
# Dry-run (no ejecuta, solo muestra SQL)
poetry run alembic upgrade head --sql
```

---

## 📊 Ejemplo Completo de Setup

```bash
# 1. Crear base de datos
createdb -U YOUR_DB_USER ai_goals_tracker

# 2. Habilitar pgvector
psql -U YOUR_DB_USER -d ai_goals_tracker << EOF
CREATE EXTENSION vector;
SELECT * FROM pg_extension WHERE extname = 'vector';
EOF

# 3. Ver estado de migraciones (debería estar vacío)
cd backend
./migrate.sh current

# 4. Aplicar todas las migraciones
./migrate.sh upgrade

# 5. Verificar tablas creadas
psql -U YOUR_DB_USER -d ai_goals_tracker -c "\dt"

# 6. Verificar embeddings table con pgvector
psql -U YOUR_DB_USER -d ai_goals_tracker -c "\d embeddings"

# 7. Ver historial de migraciones
./migrate.sh history
```

---

## 📚 Próximos Pasos

Después de ejecutar migraciones:

1. ✅ Crear servicios CRUD para cada modelo
2. ✅ Implementar RAG tools para LangGraph
3. ✅ Crear event processors (RabbitMQ → Parquet)
4. ✅ Implementar endpoints de API
5. ✅ Conectar con VS Code Extension

---

**Versión**: 2.0.0
**Fecha**: 2025-12-28
**Total migraciones**: 7
**Estado**: ✅ Listo para ejecutar
**Integración futura**: `/proyectos/aquicreamos_2025/aqc/app` (users/courses)
