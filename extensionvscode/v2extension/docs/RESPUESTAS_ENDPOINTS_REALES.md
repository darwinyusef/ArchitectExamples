# 📡 Respuestas Reales de Endpoints - AI Goals Tracker V2

## ⚠️ Prerequisitos para Testing

### 1. Iniciar Base de Datos

```bash
# Asegurarse que PostgreSQL está corriendo
brew services start postgresql@15

# O si usas pg_ctl:
pg_ctl -D /usr/local/var/postgres start
```

### 2. Crear Base de Datos

```bash
# Conectar a PostgreSQL
psql postgres

# Crear base de datos
CREATE DATABASE ai_goals_tracker;

# Habilitar pgvector
\c ai_goals_tracker
CREATE EXTENSION IF NOT EXISTS vector;

# Salir
\q
```

### 3. Ejecutar Migraciones

```bash
cd backend

# Instalar dependencias
poetry install

# Ejecutar migraciones
./migrate.sh upgrade

# O manualmente:
poetry run alembic upgrade head
```

### 4. Iniciar Servidor

```bash
# Terminal 1: Backend
cd backend
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Variables de Entorno

```bash
export API_URL="http://localhost:8000/api/v1"
```

---

## 🧪 Testing Real de Endpoints

### Health Check (Verificar que el servidor funciona)

**Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/health" \
  -H "Content-Type: application/json"
```

**Expected Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-28T18:00:00.000Z",
  "services": {
    "database": "connected",
    "redis": "connected",
    "rabbitmq": "connected"
  }
}
```

---

## 👥 Users API

### 1. POST /users - Crear Usuario

**Request**:
```bash
curl -v -X POST "http://localhost:8000/api/v1/users" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "username": "alice",
    "full_name": "Alice Johnson",
    "password": "securepass123",
    "preferences": {
      "theme": "dark",
      "notifications": true
    }
  }'
```

**Response Real (Capturar aquí)**:
```json
{
  "id": "<GENERATED_UUID>",
  "email": "alice@example.com",
  "username": "alice",
  "full_name": "Alice Johnson",
  "is_active": true,
  "preferences": {
    "theme": "dark",
    "notifications": true
  },
  "metadata": {},
  "created_at": "<TIMESTAMP>",
  "updated_at": "<TIMESTAMP>",
  "last_login": null
}
```

**Guardar el UUID**:
```bash
export USER_ID="<UUID_FROM_RESPONSE>"
```

---

### 2. GET /users/{user_id} - Obtener Usuario

**Request**:
```bash
curl -v -X GET "http://localhost:8000/api/v1/users/${USER_ID}" \
  -H "Content-Type: application/json"
```

**Response Real**:
```json
{
  "id": "...",
  "email": "alice@example.com",
  "username": "alice",
  "full_name": "Alice Johnson",
  "is_active": true,
  "preferences": {...},
  "created_at": "...",
  "updated_at": "..."
}
```

---

### 3. GET /users/email/{email} - Obtener por Email

**Request**:
```bash
curl -v -X GET "http://localhost:8000/api/v1/users/email/alice@example.com" \
  -H "Content-Type: application/json"
```

**Response Real**:
```json
{
  "id": "...",
  "email": "alice@example.com",
  "username": "alice",
  ...
}
```

---

### 4. PUT /users/{user_id} - Actualizar Usuario

**Request**:
```bash
curl -v -X PUT "http://localhost:8000/api/v1/users/${USER_ID}" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Alice M. Johnson",
    "preferences": {
      "theme": "light",
      "notifications": false
    }
  }'
```

**Response Real**:
```json
{
  "id": "...",
  "full_name": "Alice M. Johnson",
  "preferences": {
    "theme": "light",
    "notifications": false
  },
  "updated_at": "<NEW_TIMESTAMP>",
  ...
}
```

---

## 📚 Courses API

### 1. POST /courses - Crear Curso

**Request**:
```bash
curl -v -X POST "http://localhost:8000/api/v1/courses" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python FastAPI Bootcamp",
    "description": "Learn to build production-ready REST APIs with FastAPI",
    "syllabus": {
      "week1": "FastAPI basics",
      "week2": "Database integration",
      "week3": "Authentication",
      "week4": "Deployment"
    },
    "start_date": "2025-01-15T00:00:00Z",
    "end_date": "2025-02-15T00:00:00Z",
    "metadata": {
      "level": "intermediate",
      "duration_weeks": 4
    }
  }'
```

**Response Real**:
```json
{
  "id": "<COURSE_UUID>",
  "user_id": "test-user-123",
  "title": "Python FastAPI Bootcamp",
  "description": "Learn to build production-ready REST APIs with FastAPI",
  "status": "draft",
  "syllabus": {
    "week1": "FastAPI basics",
    "week2": "Database integration",
    "week3": "Authentication",
    "week4": "Deployment"
  },
  "metadata": {
    "level": "intermediate",
    "duration_weeks": 4
  },
  "start_date": "2025-01-15T00:00:00Z",
  "end_date": "2025-02-15T00:00:00Z",
  "created_at": "<TIMESTAMP>",
  "updated_at": "<TIMESTAMP>"
}
```

**Guardar el UUID**:
```bash
export COURSE_ID="<COURSE_UUID>"
```

---

### 2. POST /courses/{course_id}/publish - Publicar Curso

**Request**:
```bash
curl -v -X POST "http://localhost:8000/api/v1/courses/${COURSE_ID}/publish" \
  -H "Content-Type: application/json"
```

**Response Real**:
```json
{
  "id": "...",
  "title": "Python FastAPI Bootcamp",
  "status": "active",
  "updated_at": "<NEW_TIMESTAMP>",
  ...
}
```

---

## 🎯 Goals API

### 1. POST /goals - Crear Goal

**Request**:
```bash
curl -v -X POST "http://localhost:8000/api/v1/goals" \
  -H "Content-Type: application/json" \
  -d '{
    "course_id": "'"${COURSE_ID}"'",
    "title": "Build Complete REST API",
    "description": "Create a production-ready REST API with authentication, CRUD operations, and deployment",
    "priority": "high",
    "validation_criteria": [
      "All endpoints have proper error handling",
      "Authentication with JWT tokens",
      "API documentation with Swagger",
      "Deployed to AWS with CI/CD"
    ],
    "due_date": "2025-02-01T00:00:00Z",
    "metadata": {
      "estimated_hours": 40,
      "difficulty": "intermediate"
    }
  }'
```

**Response Real** (⚠️ IMPORTANTE - Verificar que embedding se crea automáticamente):
```json
{
  "id": "<GOAL_UUID>",
  "user_id": "test-user-123",
  "course_id": "<COURSE_ID>",
  "title": "Build Complete REST API",
  "description": "Create a production-ready REST API with authentication...",
  "status": "pending",
  "priority": "high",
  "progress_percentage": 0.0,
  "ai_generated": false,
  "validation_criteria": {
    "criteria": [
      "All endpoints have proper error handling",
      "Authentication with JWT tokens",
      "API documentation with Swagger",
      "Deployed to AWS with CI/CD"
    ]
  },
  "metadata": {
    "estimated_hours": 40,
    "difficulty": "intermediate"
  },
  "due_date": "2025-02-01T00:00:00Z",
  "created_at": "<TIMESTAMP>",
  "updated_at": "<TIMESTAMP>",
  "started_at": null,
  "completed_at": null
}
```

**Guardar el UUID**:
```bash
export GOAL_ID="<GOAL_UUID>"
```

**Verificar Embedding Creado** (debe aparecer en tabla embeddings):
```bash
# Conectar a PostgreSQL
psql -U postgres -d ai_goals_tracker

# Verificar embedding
SELECT id, entity_type, entity_id, model, created_at
FROM embeddings
WHERE entity_type = 'goal'
ORDER BY created_at DESC
LIMIT 1;

# Debe mostrar el embedding con el goal_id recién creado
```

---

### 2. GET /goals - Listar Goals

**Request**:
```bash
curl -v -X GET "http://localhost:8000/api/v1/goals?limit=10" \
  -H "Content-Type: application/json"
```

**Response Real**:
```json
[
  {
    "id": "<GOAL_ID>",
    "title": "Build Complete REST API",
    "status": "pending",
    "priority": "high",
    "progress_percentage": 0.0,
    "created_at": "...",
    ...
  }
]
```

---

### 3. PATCH /goals/{goal_id}/progress - Actualizar Progreso

**Request**:
```bash
curl -v -X PATCH "http://localhost:8000/api/v1/goals/${GOAL_ID}/progress?progress_percentage=50.0" \
  -H "Content-Type: application/json"
```

**Response Real**:
```json
{
  "id": "<GOAL_ID>",
  "title": "Build Complete REST API",
  "status": "pending",
  "progress_percentage": 50.0,
  "updated_at": "<NEW_TIMESTAMP>",
  ...
}
```

---

### 4. PUT /goals/{goal_id} - Actualizar Status

**Request**:
```bash
curl -v -X PUT "http://localhost:8000/api/v1/goals/${GOAL_ID}" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_progress"
  }'
```

**Response Real** (⚠️ Verificar que started_at se setea automáticamente):
```json
{
  "id": "<GOAL_ID>",
  "title": "Build Complete REST API",
  "status": "in_progress",
  "progress_percentage": 50.0,
  "started_at": "<TIMESTAMP>",
  "updated_at": "<NEW_TIMESTAMP>",
  ...
}
```

---

## ✅ Tasks API

### 1. POST /tasks - Crear Task

**Request**:
```bash
curl -v -X POST "http://localhost:8000/api/v1/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "goal_id": "'"${GOAL_ID}"'",
    "title": "Implement User Authentication",
    "description": "Add JWT-based authentication with login, register, and token refresh endpoints",
    "task_type": "code",
    "priority": 1,
    "estimated_hours": 8.0,
    "dependencies": [],
    "metadata": {
      "technologies": ["FastAPI", "JWT", "bcrypt"],
      "files_to_create": ["auth.py", "security.py"]
    }
  }'
```

**Response Real** (⚠️ Verificar embedding creado):
```json
{
  "id": "<TASK_UUID>",
  "goal_id": "<GOAL_ID>",
  "user_id": "test-user-123",
  "title": "Implement User Authentication",
  "description": "Add JWT-based authentication...",
  "task_type": "code",
  "status": "todo",
  "priority": 1,
  "estimated_hours": 8.0,
  "actual_hours": null,
  "dependencies": [],
  "metadata": {
    "technologies": ["FastAPI", "JWT", "bcrypt"],
    "files_to_create": ["auth.py", "security.py"]
  },
  "validation_result": null,
  "ai_feedback": null,
  "created_at": "<TIMESTAMP>",
  "updated_at": "<TIMESTAMP>",
  "started_at": null,
  "completed_at": null
}
```

**Guardar el UUID**:
```bash
export TASK_ID="<TASK_UUID>"
```

---

### 2. PUT /tasks/{task_id} - Actualizar Task

**Request**:
```bash
curl -v -X PUT "http://localhost:8000/api/v1/tasks/${TASK_ID}" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_progress",
    "actual_hours": 3.5
  }'
```

**Response Real** (⚠️ Verificar que started_at se setea):
```json
{
  "id": "<TASK_ID>",
  "title": "Implement User Authentication",
  "status": "in_progress",
  "actual_hours": 3.5,
  "started_at": "<TIMESTAMP>",
  "updated_at": "<NEW_TIMESTAMP>",
  ...
}
```

---

## 📸 Code Snapshots API

### 1. POST /code-snapshots - Crear Snapshot

**Request**:
```bash
curl -v -X POST "http://localhost:8000/api/v1/code-snapshots" \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "'"${TASK_ID}"'",
    "file_path": "app/api/auth.py",
    "language": "python",
    "code_content": "from fastapi import APIRouter, Depends, HTTPException\nfrom app.core.security import create_access_token\n\nrouter = APIRouter()\n\n@router.post(\"/login\")\nasync def login(username: str, password: str):\n    # Validate credentials\n    if not validate_user(username, password):\n        raise HTTPException(status_code=401)\n    \n    token = create_access_token({\"sub\": username})\n    return {\"access_token\": token}",
    "metadata": {
      "lines_of_code": 12,
      "complexity": "low"
    }
  }'
```

**Response Real** (⚠️ Verificar embedding del código creado):
```json
{
  "id": "<SNAPSHOT_UUID>",
  "task_id": "<TASK_ID>",
  "user_id": "test-user-123",
  "file_path": "app/api/auth.py",
  "language": "python",
  "code_content": "from fastapi import APIRouter...",
  "diff_from_previous": null,
  "validation_passed": null,
  "validation_score": null,
  "validation_feedback": null,
  "issues_found": null,
  "metadata": {
    "lines_of_code": 12,
    "complexity": "low"
  },
  "created_at": "<TIMESTAMP>",
  "updated_at": "<TIMESTAMP>"
}
```

**Guardar el UUID**:
```bash
export SNAPSHOT_ID="<SNAPSHOT_UUID>"
```

**Verificar Embedding Código**:
```sql
SELECT id, entity_type, entity_id, model
FROM embeddings
WHERE entity_type = 'code_snapshot'
ORDER BY created_at DESC
LIMIT 1;
```

---

### 2. PATCH /code-snapshots/{snapshot_id}/validation - Validar Código

**Request**:
```bash
curl -v -X PATCH "http://localhost:8000/api/v1/code-snapshots/${SNAPSHOT_ID}/validation" \
  -H "Content-Type: application/json" \
  -d '{
    "validation_passed": true,
    "validation_score": 0.85,
    "validation_feedback": "Good code structure. Consider:\n- Adding type hints\n- Using OAuth2PasswordRequestForm\n- Adding rate limiting",
    "issues_found": [
      {
        "type": "style",
        "severity": "low",
        "message": "Missing type hints on line 7",
        "line": 7
      },
      {
        "type": "security",
        "severity": "medium",
        "message": "Consider rate limiting",
        "line": 6
      }
    ]
  }'
```

**Response Real**:
```json
{
  "id": "<SNAPSHOT_ID>",
  "task_id": "<TASK_ID>",
  "file_path": "app/api/auth.py",
  "language": "python",
  "validation_passed": true,
  "validation_score": 0.85,
  "validation_feedback": "Good code structure. Consider:\n- Adding type hints...",
  "issues_found": [
    {
      "type": "style",
      "severity": "low",
      "message": "Missing type hints on line 7",
      "line": 7
    },
    {
      "type": "security",
      "severity": "medium",
      "message": "Consider rate limiting",
      "line": 6
    }
  ],
  "updated_at": "<NEW_TIMESTAMP>",
  ...
}
```

---

## 📅 Events API

### 1. POST /events - Crear Event

**Request**:
```bash
curl -v -X POST "http://localhost:8000/api/v1/events" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "GOAL_CREATED",
    "entity_type": "goal",
    "entity_id": "'"${GOAL_ID}"'",
    "event_data": {
      "title": "Build Complete REST API",
      "status": "pending",
      "priority": "high"
    },
    "metadata": {
      "source": "api",
      "ip_address": "127.0.0.1"
    }
  }'
```

**Response Real** (⚠️ Verificar triple persistencia):
```json
{
  "id": "<EVENT_UUID>",
  "user_id": "test-user-123",
  "event_type": "goal_created",
  "entity_type": "goal",
  "entity_id": "<GOAL_ID>",
  "event_data": {
    "title": "Build Complete REST API",
    "status": "pending",
    "priority": "high"
  },
  "metadata": {
    "source": "api",
    "ip_address": "127.0.0.1"
  },
  "timestamp": "<TIMESTAMP>"
}
```

**Verificar Triple Persistencia**:

1. **PostgreSQL**:
```sql
SELECT id, event_type, entity_type, entity_id
FROM events
ORDER BY timestamp DESC
LIMIT 1;
```

2. **Parquet** (verificar archivo):
```bash
ls -lh backend/data/events/parquet/goal_created/2025/12/28/
# Debe existir events.parquet
```

3. **RabbitMQ** (verificar en UI si está disponible):
```
http://localhost:15672
# Exchange: events
# Routing key: goal_created.goal
```

---

### 2. GET /events/entities/{type}/{id}/history - Historial

**Request**:
```bash
curl -v -X GET "http://localhost:8000/api/v1/events/entities/goal/${GOAL_ID}/history" \
  -H "Content-Type: application/json"
```

**Response Real**:
```json
[
  {
    "id": "<EVENT_ID>",
    "user_id": "test-user-123",
    "event_type": "goal_created",
    "entity_type": "goal",
    "entity_id": "<GOAL_ID>",
    "event_data": {
      "title": "Build Complete REST API",
      "status": "pending"
    },
    "timestamp": "<TIMESTAMP_1>"
  },
  {
    "id": "<EVENT_ID_2>",
    "event_type": "goal_updated",
    "entity_type": "goal",
    "entity_id": "<GOAL_ID>",
    "event_data": {
      "status": "in_progress",
      "progress_percentage": 50.0
    },
    "timestamp": "<TIMESTAMP_2>"
  }
]
```

---

## 🔍 Verificaciones Importantes

### 1. Embeddings RAG

**Verificar que se crean automáticamente**:
```sql
-- Contar embeddings por tipo
SELECT
    entity_type,
    COUNT(*) as total,
    model
FROM embeddings
GROUP BY entity_type, model
ORDER BY entity_type;

-- Debe mostrar:
-- entity_type   | total | model
-- --------------+-------+-------------------------
-- goal          |     1 | text-embedding-3-small
-- task          |     1 | text-embedding-3-small
-- code_snapshot |     1 | text-embedding-3-small
```

### 2. Índice HNSW

**Verificar que el índice existe**:
```sql
SELECT
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename = 'embeddings'
  AND indexname LIKE '%hnsw%';
```

### 3. Event Sourcing

**Verificar eventos en PostgreSQL**:
```sql
SELECT
    event_type,
    entity_type,
    COUNT(*) as total
FROM events
GROUP BY event_type, entity_type
ORDER BY event_type;
```

**Verificar archivos Parquet**:
```bash
find backend/data/events/parquet -name "*.parquet" -type f
```

---

## 📝 Template para Capturar Respuestas

### Para cada endpoint probado:

```markdown
### Endpoint: [METHOD] [PATH]

**Request ejecutado**:
```bash
<curl command>
```

**Response Status**: [HTTP_CODE]

**Response Headers**:
```
content-type: application/json
content-length: XXX
```

**Response Body**:
```json
<JSON response>
```

**Timing**:
- Total time: XXms
- Connection time: XXms
- Time to first byte: XXms

**Base de Datos - Verificación**:
```sql
<query para verificar>
```

**Resultado**:
```
<resultado de la query>
```

**Embeddings creados**: [SI/NO]
**Events creados**: [SI/NO]
**Parquet creado**: [SI/NO]

---
```

---

## 🚀 Script de Testing Automatizado

Crear este script para ejecutar todos los tests:

```bash
#!/bin/bash
# tests/run_integration_tests.sh

set -e  # Exit on error

API_URL="http://localhost:8000/api/v1"

echo "🧪 AI Goals Tracker V2 - Integration Tests"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Function to test endpoint
test_endpoint() {
    local METHOD=$1
    local PATH=$2
    local DATA=$3
    local DESCRIPTION=$4

    echo -e "${YELLOW}Testing:${NC} $DESCRIPTION"
    echo "  $METHOD $PATH"

    RESPONSE=$(curl -s -w "\n%{http_code}" -X $METHOD "$API_URL$PATH" \
        -H "Content-Type: application/json" \
        ${DATA:+-d "$DATA"})

    HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)
    BODY=$(echo "$RESPONSE" | head -n -1)

    if [[ $HTTP_CODE -ge 200 && $HTTP_CODE -lt 300 ]]; then
        echo -e "  ${GREEN}✓ PASSED${NC} (HTTP $HTTP_CODE)"
        echo "  Response: $BODY" | head -c 100
        echo "..."
        ((TESTS_PASSED++))
    else
        echo -e "  ${RED}✗ FAILED${NC} (HTTP $HTTP_CODE)"
        echo "  Response: $BODY"
        ((TESTS_FAILED++))
    fi
    echo ""
}

# Run tests
echo "1️⃣ Health Check"
test_endpoint "GET" "/health" "" "Health endpoint"

echo "2️⃣ Create User"
USER_RESPONSE=$(curl -s -X POST "$API_URL/users" \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","username":"testuser","full_name":"Test User","password":"password123"}')
USER_ID=$(echo $USER_RESPONSE | jq -r '.id')
echo "Created user: $USER_ID"

echo "3️⃣ Create Course"
COURSE_RESPONSE=$(curl -s -X POST "$API_URL/courses" \
    -H "Content-Type: application/json" \
    -d '{"title":"Test Course","description":"Test description"}')
COURSE_ID=$(echo $COURSE_RESPONSE | jq -r '.id')
echo "Created course: $COURSE_ID"

echo "4️⃣ Create Goal"
GOAL_RESPONSE=$(curl -s -X POST "$API_URL/goals" \
    -H "Content-Type: application/json" \
    -d "{\"course_id\":\"$COURSE_ID\",\"title\":\"Test Goal\",\"description\":\"Test goal description\",\"priority\":\"high\"}")
GOAL_ID=$(echo $GOAL_RESPONSE | jq -r '.id')
echo "Created goal: $GOAL_ID"

# ... más tests

echo ""
echo "=========================================="
echo -e "${GREEN}Tests Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Tests Failed: $TESTS_FAILED${NC}"
echo "=========================================="

if [[ $TESTS_FAILED -gt 0 ]]; then
    exit 1
fi
```

---

**Estado**: ⚠️ **Requiere ejecución del servidor para capturar respuestas reales**

**Siguiente paso**:
1. Ejecutar `migrate.sh upgrade`
2. Iniciar servidor
3. Ejecutar cada curl y capturar respuestas
4. Verificar embeddings, events y parquet
5. Documentar resultados reales
