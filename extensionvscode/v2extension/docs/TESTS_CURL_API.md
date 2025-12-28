# 🧪 Tests de Integración con cURL - AI Goals Tracker V2

## 📋 Índice

1. [Setup](#setup)
2. [Users API](#users-api)
3. [Courses API](#courses-api)
4. [Goals API](#goals-api)
5. [Tasks API](#tasks-api)
6. [Code Snapshots API](#code-snapshots-api)
7. [Events API](#events-api)
8. [WebSocket Test con JavaScript](#websocket-test)

---

## Setup

### Iniciar el servidor

```bash
cd backend
poetry install
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Variables de entorno

```bash
export API_URL="http://localhost:8000/api/v1"
export USER_ID="test-user-123"
```

---

## Users API

### 1. Crear Usuario

**Request:**
```bash
curl -X POST "${API_URL}/users" \
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

**Expected Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "alice@example.com",
  "username": "alice",
  "full_name": "Alice Johnson",
  "is_active": true,
  "preferences": {
    "theme": "dark",
    "notifications": true
  },
  "metadata": {},
  "created_at": "2025-12-28T15:30:00.000Z",
  "updated_at": "2025-12-28T15:30:00.000Z",
  "last_login": null
}
```

### 2. Obtener Usuario por ID

**Request:**
```bash
USER_ID="550e8400-e29b-41d4-a716-446655440000"

curl -X GET "${API_URL}/users/${USER_ID}" \
  -H "Content-Type: application/json"
```

**Expected Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "alice@example.com",
  "username": "alice",
  "full_name": "Alice Johnson",
  "is_active": true,
  "preferences": {
    "theme": "dark",
    "notifications": true
  },
  "created_at": "2025-12-28T15:30:00.000Z",
  "updated_at": "2025-12-28T15:30:00.000Z"
}
```

### 3. Obtener Usuario por Email

**Request:**
```bash
curl -X GET "${API_URL}/users/email/alice@example.com" \
  -H "Content-Type: application/json"
```

**Expected Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "alice@example.com",
  "username": "alice",
  "full_name": "Alice Johnson",
  "is_active": true
}
```

### 4. Actualizar Usuario

**Request:**
```bash
curl -X PUT "${API_URL}/users/${USER_ID}" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Alice M. Johnson",
    "preferences": {
      "theme": "light",
      "notifications": false
    }
  }'
```

**Expected Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "alice@example.com",
  "username": "alice",
  "full_name": "Alice M. Johnson",
  "is_active": true,
  "preferences": {
    "theme": "light",
    "notifications": false
  },
  "updated_at": "2025-12-28T15:35:00.000Z"
}
```

### 5. Desactivar Usuario

**Request:**
```bash
curl -X POST "${API_URL}/users/${USER_ID}/deactivate" \
  -H "Content-Type: application/json"
```

**Expected Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "alice@example.com",
  "username": "alice",
  "is_active": false,
  "updated_at": "2025-12-28T15:40:00.000Z"
}
```

---

## Courses API

### 1. Crear Curso

**Request:**
```bash
curl -X POST "${API_URL}/courses" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python FastAPI Bootcamp",
    "description": "Learn to build production-ready REST APIs with FastAPI, PostgreSQL, and Docker",
    "syllabus": {
      "week1": "FastAPI basics and routing",
      "week2": "Database integration with SQLAlchemy",
      "week3": "Authentication and authorization",
      "week4": "Deployment and monitoring"
    },
    "start_date": "2025-01-15T00:00:00Z",
    "end_date": "2025-02-15T00:00:00Z",
    "metadata": {
      "level": "intermediate",
      "duration_weeks": 4,
      "rag_config": {
        "default_scope": "course",
        "allow_global_search": true
      }
    }
  }'
```

**Expected Response (201 Created):**
```json
{
  "id": "course-123-abc",
  "user_id": "test-user-123",
  "title": "Python FastAPI Bootcamp",
  "description": "Learn to build production-ready REST APIs with FastAPI, PostgreSQL, and Docker",
  "status": "draft",
  "syllabus": {
    "week1": "FastAPI basics and routing",
    "week2": "Database integration with SQLAlchemy",
    "week3": "Authentication and authorization",
    "week4": "Deployment and monitoring"
  },
  "metadata": {
    "level": "intermediate",
    "duration_weeks": 4,
    "rag_config": {
      "default_scope": "course",
      "allow_global_search": true
    }
  },
  "start_date": "2025-01-15T00:00:00Z",
  "end_date": "2025-02-15T00:00:00Z",
  "created_at": "2025-12-28T15:45:00.000Z"
}
```

### 2. Obtener Curso

**Request:**
```bash
COURSE_ID="course-123-abc"

curl -X GET "${API_URL}/courses/${COURSE_ID}" \
  -H "Content-Type: application/json"
```

**Expected Response (200 OK):**
```json
{
  "id": "course-123-abc",
  "title": "Python FastAPI Bootcamp",
  "description": "Learn to build production-ready REST APIs...",
  "status": "draft",
  "created_at": "2025-12-28T15:45:00.000Z"
}
```

### 3. Listar Cursos

**Request:**
```bash
curl -X GET "${API_URL}/courses?status_filter=active&limit=10" \
  -H "Content-Type: application/json"
```

**Expected Response (200 OK):**
```json
[
  {
    "id": "course-123-abc",
    "title": "Python FastAPI Bootcamp",
    "status": "active",
    "created_at": "2025-12-28T15:45:00.000Z"
  }
]
```

### 4. Actualizar Curso

**Request:**
```bash
curl -X PUT "${API_URL}/courses/${COURSE_ID}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Advanced Python FastAPI Bootcamp",
    "description": "Master production-ready REST APIs with FastAPI"
  }'
```

**Expected Response (200 OK):**
```json
{
  "id": "course-123-abc",
  "title": "Advanced Python FastAPI Bootcamp",
  "description": "Master production-ready REST APIs with FastAPI",
  "updated_at": "2025-12-28T16:00:00.000Z"
}
```

### 5. Publicar Curso

**Request:**
```bash
curl -X POST "${API_URL}/courses/${COURSE_ID}/publish" \
  -H "Content-Type: application/json"
```

**Expected Response (200 OK):**
```json
{
  "id": "course-123-abc",
  "title": "Advanced Python FastAPI Bootcamp",
  "status": "active",
  "updated_at": "2025-12-28T16:05:00.000Z"
}
```

### 6. Archivar Curso

**Request:**
```bash
curl -X POST "${API_URL}/courses/${COURSE_ID}/archive" \
  -H "Content-Type: application/json"
```

**Expected Response (200 OK):**
```json
{
  "id": "course-123-abc",
  "status": "archived",
  "updated_at": "2025-12-28T16:10:00.000Z"
}
```

---

## Goals API

### 1. Crear Goal

**Request:**
```bash
curl -X POST "${API_URL}/goals" \
  -H "Content-Type: application/json" \
  -d '{
    "course_id": "course-123-abc",
    "title": "Build Complete REST API",
    "description": "Create a production-ready REST API with authentication, CRUD operations, and deployment to AWS",
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

**Expected Response (201 Created):**
```json
{
  "id": "goal-456-def",
  "user_id": "test-user-123",
  "course_id": "course-123-abc",
  "title": "Build Complete REST API",
  "description": "Create a production-ready REST API with authentication, CRUD operations, and deployment to AWS",
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
  "created_at": "2025-12-28T16:15:00.000Z",
  "started_at": null,
  "completed_at": null
}
```

### 2. Obtener Goal

**Request:**
```bash
GOAL_ID="goal-456-def"

curl -X GET "${API_URL}/goals/${GOAL_ID}" \
  -H "Content-Type: application/json"
```

**Expected Response (200 OK):**
```json
{
  "id": "goal-456-def",
  "title": "Build Complete REST API",
  "description": "Create a production-ready REST API...",
  "status": "pending",
  "priority": "high",
  "progress_percentage": 0.0,
  "created_at": "2025-12-28T16:15:00.000Z"
}
```

### 3. Listar Goals

**Request:**
```bash
# Todos los goals del usuario
curl -X GET "${API_URL}/goals?limit=20" \
  -H "Content-Type: application/json"

# Goals de un curso específico
curl -X GET "${API_URL}/goals?course_id=${COURSE_ID}&limit=20" \
  -H "Content-Type: application/json"

# Goals por status
curl -X GET "${API_URL}/goals?status_filter=in_progress&limit=20" \
  -H "Content-Type: application/json"
```

**Expected Response (200 OK):**
```json
[
  {
    "id": "goal-456-def",
    "title": "Build Complete REST API",
    "status": "pending",
    "priority": "high",
    "progress_percentage": 0.0,
    "created_at": "2025-12-28T16:15:00.000Z"
  },
  {
    "id": "goal-789-ghi",
    "title": "Deploy to AWS",
    "status": "in_progress",
    "priority": "medium",
    "progress_percentage": 45.0,
    "created_at": "2025-12-27T10:00:00.000Z"
  }
]
```

### 4. Actualizar Goal

**Request:**
```bash
curl -X PUT "${API_URL}/goals/${GOAL_ID}" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_progress",
    "progress_percentage": 25.0
  }'
```

**Expected Response (200 OK):**
```json
{
  "id": "goal-456-def",
  "title": "Build Complete REST API",
  "status": "in_progress",
  "priority": "high",
  "progress_percentage": 25.0,
  "started_at": "2025-12-28T16:20:00.000Z",
  "updated_at": "2025-12-28T16:20:00.000Z"
}
```

### 5. Actualizar Progreso

**Request:**
```bash
curl -X PATCH "${API_URL}/goals/${GOAL_ID}/progress?progress_percentage=75.5" \
  -H "Content-Type: application/json"
```

**Expected Response (200 OK):**
```json
{
  "id": "goal-456-def",
  "title": "Build Complete REST API",
  "status": "in_progress",
  "progress_percentage": 75.5,
  "updated_at": "2025-12-28T16:25:00.000Z"
}
```

### 6. Completar Goal

**Request:**
```bash
curl -X PATCH "${API_URL}/goals/${GOAL_ID}/progress?progress_percentage=100" \
  -H "Content-Type: application/json"
```

**Expected Response (200 OK):**
```json
{
  "id": "goal-456-def",
  "title": "Build Complete REST API",
  "status": "completed",
  "progress_percentage": 100.0,
  "completed_at": "2025-12-28T16:30:00.000Z",
  "updated_at": "2025-12-28T16:30:00.000Z"
}
```

### 7. Eliminar Goal

**Request:**
```bash
curl -X DELETE "${API_URL}/goals/${GOAL_ID}" \
  -H "Content-Type: application/json"
```

**Expected Response (204 No Content):**
```
(No body)
```

---

## Tasks API

### 1. Crear Task

**Request:**
```bash
curl -X POST "${API_URL}/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "goal_id": "goal-456-def",
    "title": "Implement User Authentication",
    "description": "Add JWT-based authentication with login, register, and token refresh endpoints",
    "task_type": "code",
    "priority": 1,
    "estimated_hours": 8.0,
    "dependencies": [],
    "metadata": {
      "technologies": ["FastAPI", "JWT", "bcrypt"],
      "files_to_create": ["auth.py", "security.py", "schemas/auth.py"]
    }
  }'
```

**Expected Response (201 Created):**
```json
{
  "id": "task-111-aaa",
  "goal_id": "goal-456-def",
  "user_id": "test-user-123",
  "title": "Implement User Authentication",
  "description": "Add JWT-based authentication with login, register, and token refresh endpoints",
  "task_type": "code",
  "status": "todo",
  "priority": 1,
  "estimated_hours": 8.0,
  "actual_hours": null,
  "dependencies": [],
  "metadata": {
    "technologies": ["FastAPI", "JWT", "bcrypt"],
    "files_to_create": ["auth.py", "security.py", "schemas/auth.py"]
  },
  "validation_result": null,
  "ai_feedback": null,
  "created_at": "2025-12-28T16:35:00.000Z",
  "started_at": null,
  "completed_at": null
}
```

### 2. Obtener Task

**Request:**
```bash
TASK_ID="task-111-aaa"

curl -X GET "${API_URL}/tasks/${TASK_ID}" \
  -H "Content-Type: application/json"
```

**Expected Response (200 OK):**
```json
{
  "id": "task-111-aaa",
  "goal_id": "goal-456-def",
  "title": "Implement User Authentication",
  "description": "Add JWT-based authentication...",
  "task_type": "code",
  "status": "todo",
  "priority": 1,
  "created_at": "2025-12-28T16:35:00.000Z"
}
```

### 3. Listar Tasks

**Request:**
```bash
# Todas las tasks del usuario
curl -X GET "${API_URL}/tasks?limit=20" \
  -H "Content-Type: application/json"

# Tasks de un goal específico
curl -X GET "${API_URL}/tasks?goal_id=${GOAL_ID}&limit=20" \
  -H "Content-Type: application/json"

# Tasks por status
curl -X GET "${API_URL}/tasks?status_filter=in_progress&limit=20" \
  -H "Content-Type: application/json"

# Tasks por tipo
curl -X GET "${API_URL}/tasks?task_type=code&limit=20" \
  -H "Content-Type: application/json"
```

**Expected Response (200 OK):**
```json
[
  {
    "id": "task-111-aaa",
    "goal_id": "goal-456-def",
    "title": "Implement User Authentication",
    "task_type": "code",
    "status": "todo",
    "priority": 1,
    "created_at": "2025-12-28T16:35:00.000Z"
  },
  {
    "id": "task-222-bbb",
    "goal_id": "goal-456-def",
    "title": "Write API Documentation",
    "task_type": "documentation",
    "status": "in_progress",
    "priority": 2,
    "created_at": "2025-12-28T16:40:00.000Z"
  }
]
```

### 4. Actualizar Task

**Request:**
```bash
curl -X PUT "${API_URL}/tasks/${TASK_ID}" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_progress",
    "actual_hours": 3.5
  }'
```

**Expected Response (200 OK):**
```json
{
  "id": "task-111-aaa",
  "title": "Implement User Authentication",
  "status": "in_progress",
  "actual_hours": 3.5,
  "started_at": "2025-12-28T16:45:00.000Z",
  "updated_at": "2025-12-28T16:45:00.000Z"
}
```

### 5. Completar Task

**Request:**
```bash
curl -X PUT "${API_URL}/tasks/${TASK_ID}" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "completed",
    "actual_hours": 7.5,
    "validation_result": {
      "passed": true,
      "score": 0.95,
      "tests_passed": 12,
      "tests_failed": 0
    },
    "ai_feedback": "Excellent implementation! JWT tokens properly configured with secure secrets. Consider adding rate limiting to login endpoint."
  }'
```

**Expected Response (200 OK):**
```json
{
  "id": "task-111-aaa",
  "title": "Implement User Authentication",
  "status": "completed",
  "actual_hours": 7.5,
  "validation_result": {
    "passed": true,
    "score": 0.95,
    "tests_passed": 12,
    "tests_failed": 0
  },
  "ai_feedback": "Excellent implementation! JWT tokens properly configured with secure secrets. Consider adding rate limiting to login endpoint.",
  "completed_at": "2025-12-28T17:00:00.000Z",
  "updated_at": "2025-12-28T17:00:00.000Z"
}
```

### 6. Eliminar Task

**Request:**
```bash
curl -X DELETE "${API_URL}/tasks/${TASK_ID}" \
  -H "Content-Type: application/json"
```

**Expected Response (204 No Content):**
```
(No body)
```

---

## Code Snapshots API

### 1. Crear Code Snapshot

**Request:**
```bash
curl -X POST "${API_URL}/code-snapshots" \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "task-111-aaa",
    "file_path": "app/api/auth.py",
    "language": "python",
    "code_content": "from fastapi import APIRouter, Depends, HTTPException\nfrom app.core.security import create_access_token\n\nrouter = APIRouter()\n\n@router.post(\"/login\")\nasync def login(username: str, password: str):\n    # Validate credentials\n    if not validate_user(username, password):\n        raise HTTPException(status_code=401)\n    \n    token = create_access_token({\"sub\": username})\n    return {\"access_token\": token}",
    "diff_from_previous": null,
    "metadata": {
      "lines_of_code": 12,
      "complexity": "low",
      "imports": ["fastapi", "app.core.security"]
    }
  }'
```

**Expected Response (201 Created):**
```json
{
  "id": "snapshot-333-ccc",
  "task_id": "task-111-aaa",
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
    "complexity": "low",
    "imports": ["fastapi", "app.core.security"]
  },
  "created_at": "2025-12-28T17:05:00.000Z"
}
```

### 2. Obtener Snapshot

**Request:**
```bash
SNAPSHOT_ID="snapshot-333-ccc"

curl -X GET "${API_URL}/code-snapshots/${SNAPSHOT_ID}" \
  -H "Content-Type: application/json"
```

**Expected Response (200 OK):**
```json
{
  "id": "snapshot-333-ccc",
  "task_id": "task-111-aaa",
  "file_path": "app/api/auth.py",
  "language": "python",
  "code_content": "from fastapi import APIRouter...",
  "created_at": "2025-12-28T17:05:00.000Z"
}
```

### 3. Listar Snapshots

**Request:**
```bash
# Todos los snapshots del usuario
curl -X GET "${API_URL}/code-snapshots?limit=20" \
  -H "Content-Type: application/json"

# Snapshots de una task
curl -X GET "${API_URL}/code-snapshots?task_id=${TASK_ID}&limit=20" \
  -H "Content-Type: application/json"

# Snapshots por lenguaje
curl -X GET "${API_URL}/code-snapshots?language=python&limit=20" \
  -H "Content-Type: application/json"

# Solo código validado
curl -X GET "${API_URL}/code-snapshots?validated_only=true&limit=20" \
  -H "Content-Type: application/json"
```

**Expected Response (200 OK):**
```json
[
  {
    "id": "snapshot-333-ccc",
    "task_id": "task-111-aaa",
    "file_path": "app/api/auth.py",
    "language": "python",
    "validation_passed": true,
    "validation_score": 0.95,
    "created_at": "2025-12-28T17:05:00.000Z"
  }
]
```

### 4. Actualizar Validación

**Request:**
```bash
curl -X PATCH "${API_URL}/code-snapshots/${SNAPSHOT_ID}/validation" \
  -H "Content-Type: application/json" \
  -d '{
    "validation_passed": true,
    "validation_score": 0.92,
    "validation_feedback": "Code quality: Good\n\nStrengths:\n- Proper error handling\n- Clean imports\n- Follows FastAPI conventions\n\nSuggestions:\n- Add type hints to function parameters\n- Consider using OAuth2PasswordRequestForm\n- Add rate limiting decorator",
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
        "message": "Consider rate limiting for login endpoint",
        "line": 6
      }
    ]
  }'
```

**Expected Response (200 OK):**
```json
{
  "id": "snapshot-333-ccc",
  "task_id": "task-111-aaa",
  "file_path": "app/api/auth.py",
  "language": "python",
  "validation_passed": true,
  "validation_score": 0.92,
  "validation_feedback": "Code quality: Good\n\nStrengths:\n- Proper error handling...",
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
      "message": "Consider rate limiting for login endpoint",
      "line": 6
    }
  ],
  "updated_at": "2025-12-28T17:10:00.000Z"
}
```

### 5. Obtener Último Snapshot de Task

**Request:**
```bash
curl -X GET "${API_URL}/code-snapshots/tasks/${TASK_ID}/latest" \
  -H "Content-Type: application/json"
```

**Expected Response (200 OK):**
```json
{
  "id": "snapshot-333-ccc",
  "task_id": "task-111-aaa",
  "file_path": "app/api/auth.py",
  "language": "python",
  "code_content": "from fastapi import APIRouter...",
  "validation_passed": true,
  "validation_score": 0.92,
  "created_at": "2025-12-28T17:05:00.000Z"
}
```

### 6. Eliminar Snapshot

**Request:**
```bash
curl -X DELETE "${API_URL}/code-snapshots/${SNAPSHOT_ID}" \
  -H "Content-Type: application/json"
```

**Expected Response (204 No Content):**
```
(No body)
```

---

## Events API

### 1. Crear Event

**Request:**
```bash
curl -X POST "${API_URL}/events" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "GOAL_CREATED",
    "entity_type": "goal",
    "entity_id": "goal-456-def",
    "event_data": {
      "title": "Build Complete REST API",
      "status": "pending",
      "priority": "high",
      "course_id": "course-123-abc"
    },
    "metadata": {
      "source": "web_app",
      "ip_address": "192.168.1.100",
      "user_agent": "Mozilla/5.0..."
    }
  }'
```

**Expected Response (201 Created):**
```json
{
  "id": "event-777-xxx",
  "user_id": "test-user-123",
  "event_type": "goal_created",
  "entity_type": "goal",
  "entity_id": "goal-456-def",
  "event_data": {
    "title": "Build Complete REST API",
    "status": "pending",
    "priority": "high",
    "course_id": "course-123-abc"
  },
  "metadata": {
    "source": "web_app",
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0..."
  },
  "timestamp": "2025-12-28T17:15:00.000Z"
}
```

**Note**: Este evento se guarda en:
1. PostgreSQL (tabla events)
2. Parquet (backend/data/events/parquet/goal_created/2025/12/28/events.parquet)
3. RabbitMQ (exchange: events, routing key: goal_created.goal)

### 2. Obtener Event

**Request:**
```bash
EVENT_ID="event-777-xxx"

curl -X GET "${API_URL}/events/${EVENT_ID}" \
  -H "Content-Type: application/json"
```

**Expected Response (200 OK):**
```json
{
  "id": "event-777-xxx",
  "user_id": "test-user-123",
  "event_type": "goal_created",
  "entity_type": "goal",
  "entity_id": "goal-456-def",
  "event_data": {
    "title": "Build Complete REST API",
    "status": "pending"
  },
  "timestamp": "2025-12-28T17:15:00.000Z"
}
```

### 3. Listar Events

**Request:**
```bash
# Todos los eventos
curl -X GET "${API_URL}/events?limit=20" \
  -H "Content-Type: application/json"

# Eventos de un usuario
curl -X GET "${API_URL}/events?user_id_filter=${USER_ID}&limit=20" \
  -H "Content-Type: application/json"

# Eventos por tipo
curl -X GET "${API_URL}/events?event_type=goal_created&limit=20" \
  -H "Content-Type: application/json"

# Eventos de una entidad
curl -X GET "${API_URL}/events?entity_type=goal&entity_id=${GOAL_ID}&limit=20" \
  -H "Content-Type: application/json"

# Eventos por rango de fechas
curl -X GET "${API_URL}/events?start_date=2025-12-01T00:00:00Z&end_date=2025-12-31T23:59:59Z&limit=50" \
  -H "Content-Type: application/json"
```

**Expected Response (200 OK):**
```json
[
  {
    "id": "event-777-xxx",
    "user_id": "test-user-123",
    "event_type": "goal_created",
    "entity_type": "goal",
    "entity_id": "goal-456-def",
    "timestamp": "2025-12-28T17:15:00.000Z"
  },
  {
    "id": "event-888-yyy",
    "user_id": "test-user-123",
    "event_type": "task_completed",
    "entity_type": "task",
    "entity_id": "task-111-aaa",
    "timestamp": "2025-12-28T17:00:00.000Z"
  }
]
```

### 4. Obtener Historial de Entidad

**Request:**
```bash
curl -X GET "${API_URL}/events/entities/goal/${GOAL_ID}/history" \
  -H "Content-Type: application/json"
```

**Expected Response (200 OK):**
```json
[
  {
    "id": "event-777-xxx",
    "event_type": "goal_created",
    "event_data": {
      "title": "Build Complete REST API",
      "status": "pending"
    },
    "timestamp": "2025-12-28T16:15:00.000Z"
  },
  {
    "id": "event-888-yyy",
    "event_type": "goal_updated",
    "event_data": {
      "status": "in_progress",
      "progress_percentage": 25.0
    },
    "timestamp": "2025-12-28T16:20:00.000Z"
  },
  {
    "id": "event-999-zzz",
    "event_type": "goal_completed",
    "event_data": {
      "status": "completed",
      "progress_percentage": 100.0
    },
    "timestamp": "2025-12-28T16:30:00.000Z"
  }
]
```

### 5. Replay Events (Reconstruir Estado)

**Request:**
```bash
curl -X POST "${API_URL}/events/replay" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_type": "goal",
    "entity_id": "goal-456-def",
    "target_timestamp": "2025-12-28T16:25:00Z"
  }'
```

**Expected Response (200 OK):**
```json
{
  "entity_type": "goal",
  "entity_id": "goal-456-def",
  "reconstructed_at": "2025-12-28T16:25:00Z",
  "event_count": 2,
  "state": {
    "title": "Build Complete REST API",
    "status": "in_progress",
    "progress_percentage": 25.0,
    "priority": "high",
    "course_id": "course-123-abc"
  }
}
```

**Explanation**: Este endpoint reconstruye el estado del goal como estaba a las 16:25:00, aplicando solo los eventos hasta ese momento.

---

## WebSocket Test

### Archivo: `test_websocket.html`

Crea este archivo HTML para probar WebSocket desde el navegador:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WebSocket Test - AI Goals Tracker</title>
    <style>
        body {
            font-family: 'Courier New', monospace;
            max-width: 900px;
            margin: 50px auto;
            padding: 20px;
            background: #1e1e1e;
            color: #d4d4d4;
        }
        h1 {
            color: #4ec9b0;
        }
        .container {
            background: #252526;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .status {
            padding: 10px;
            border-radius: 4px;
            margin-bottom: 10px;
            font-weight: bold;
        }
        .status.connected {
            background: #0e639c;
            color: white;
        }
        .status.disconnected {
            background: #f48771;
            color: white;
        }
        button {
            background: #0e639c;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            margin-right: 10px;
            font-size: 14px;
        }
        button:hover {
            background: #1177bb;
        }
        button:disabled {
            background: #3e3e42;
            cursor: not-allowed;
        }
        #messages {
            background: #1e1e1e;
            border: 1px solid #3e3e42;
            border-radius: 4px;
            padding: 15px;
            height: 400px;
            overflow-y: auto;
            font-size: 13px;
            line-height: 1.6;
        }
        .message {
            margin-bottom: 10px;
            padding: 8px;
            border-left: 3px solid #4ec9b0;
            background: #252526;
        }
        .message.sent {
            border-left-color: #569cd6;
        }
        .message.received {
            border-left-color: #4ec9b0;
        }
        .message.error {
            border-left-color: #f48771;
        }
        .timestamp {
            color: #858585;
            font-size: 11px;
        }
        input, textarea {
            width: 100%;
            padding: 10px;
            background: #3c3c3c;
            border: 1px solid #3e3e42;
            color: #d4d4d4;
            border-radius: 4px;
            margin-bottom: 10px;
            font-family: 'Courier New', monospace;
        }
        label {
            display: block;
            margin-bottom: 5px;
            color: #4ec9b0;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <h1>🔌 WebSocket Test - AI Goals Tracker V2</h1>

    <div class="container">
        <div id="status" class="status disconnected">
            Status: Disconnected
        </div>

        <div style="margin-bottom: 20px;">
            <label>WebSocket URL:</label>
            <input type="text" id="wsUrl" value="ws://localhost:8000/ws" />
        </div>

        <div>
            <button id="connectBtn" onclick="connect()">Connect</button>
            <button id="disconnectBtn" onclick="disconnect()" disabled>Disconnect</button>
            <button onclick="clearMessages()">Clear Messages</button>
        </div>
    </div>

    <div class="container">
        <h3 style="color: #4ec9b0;">Send Message</h3>

        <div style="margin-bottom: 20px;">
            <label>Message Type:</label>
            <select id="messageType" style="width: 100%; padding: 10px; background: #3c3c3c; border: 1px solid #3e3e42; color: #d4d4d4; border-radius: 4px;">
                <option value="ping">Ping</option>
                <option value="goal_update">Goal Update</option>
                <option value="task_update">Task Update</option>
                <option value="code_validation">Code Validation Request</option>
                <option value="custom">Custom JSON</option>
            </select>
        </div>

        <div id="customMessageDiv" style="display: none;">
            <label>Custom JSON:</label>
            <textarea id="customMessage" rows="6" placeholder='{"type": "ping", "data": {}}'></textarea>
        </div>

        <button id="sendBtn" onclick="sendMessage()" disabled>Send Message</button>

        <div style="margin-top: 20px;">
            <h4 style="color: #858585;">Quick Actions:</h4>
            <button onclick="sendPing()">Send Ping</button>
            <button onclick="sendGoalUpdate()">Send Goal Update</button>
            <button onclick="sendTaskUpdate()">Send Task Update</button>
        </div>
    </div>

    <div class="container">
        <h3 style="color: #4ec9b0;">Messages</h3>
        <div id="messages"></div>
    </div>

    <script>
        let ws = null;

        const statusEl = document.getElementById('status');
        const messagesEl = document.getElementById('messages');
        const connectBtn = document.getElementById('connectBtn');
        const disconnectBtn = document.getElementById('disconnectBtn');
        const sendBtn = document.getElementById('sendBtn');
        const messageTypeEl = document.getElementById('messageType');
        const customMessageDiv = document.getElementById('customMessageDiv');

        // Show/hide custom message textarea
        messageTypeEl.addEventListener('change', function() {
            customMessageDiv.style.display = this.value === 'custom' ? 'block' : 'none';
        });

        function connect() {
            const url = document.getElementById('wsUrl').value;

            addMessage('system', `Connecting to ${url}...`);

            ws = new WebSocket(url);

            ws.onopen = function(event) {
                addMessage('system', 'Connected to WebSocket server!', 'received');
                statusEl.textContent = 'Status: Connected';
                statusEl.className = 'status connected';
                connectBtn.disabled = true;
                disconnectBtn.disabled = false;
                sendBtn.disabled = false;
            };

            ws.onmessage = function(event) {
                try {
                    const data = JSON.parse(event.data);
                    addMessage('received', JSON.stringify(data, null, 2), 'received');
                } catch (e) {
                    addMessage('received', event.data, 'received');
                }
            };

            ws.onerror = function(error) {
                addMessage('error', 'WebSocket error occurred', 'error');
                console.error('WebSocket error:', error);
            };

            ws.onclose = function(event) {
                addMessage('system', `Disconnected from server (Code: ${event.code})`, 'error');
                statusEl.textContent = 'Status: Disconnected';
                statusEl.className = 'status disconnected';
                connectBtn.disabled = false;
                disconnectBtn.disabled = true;
                sendBtn.disabled = true;
            };
        }

        function disconnect() {
            if (ws) {
                ws.close();
                ws = null;
            }
        }

        function sendMessage() {
            if (!ws || ws.readyState !== WebSocket.OPEN) {
                alert('WebSocket is not connected!');
                return;
            }

            const messageType = messageTypeEl.value;
            let message;

            if (messageType === 'custom') {
                const customText = document.getElementById('customMessage').value;
                try {
                    message = JSON.parse(customText);
                } catch (e) {
                    alert('Invalid JSON!');
                    return;
                }
            } else {
                message = getMessageTemplate(messageType);
            }

            const messageStr = JSON.stringify(message);
            ws.send(messageStr);
            addMessage('sent', messageStr, 'sent');
        }

        function sendPing() {
            if (!ws || ws.readyState !== WebSocket.OPEN) {
                alert('WebSocket is not connected!');
                return;
            }
            const msg = { type: 'ping', timestamp: new Date().toISOString() };
            ws.send(JSON.stringify(msg));
            addMessage('sent', JSON.stringify(msg, null, 2), 'sent');
        }

        function sendGoalUpdate() {
            if (!ws || ws.readyState !== WebSocket.OPEN) {
                alert('WebSocket is not connected!');
                return;
            }
            const msg = {
                type: 'goal_update',
                data: {
                    goal_id: 'goal-456-def',
                    status: 'in_progress',
                    progress_percentage: 50.0
                }
            };
            ws.send(JSON.stringify(msg));
            addMessage('sent', JSON.stringify(msg, null, 2), 'sent');
        }

        function sendTaskUpdate() {
            if (!ws || ws.readyState !== WebSocket.OPEN) {
                alert('WebSocket is not connected!');
                return;
            }
            const msg = {
                type: 'task_update',
                data: {
                    task_id: 'task-111-aaa',
                    status: 'completed',
                    validation_result: {
                        passed: true,
                        score: 0.95
                    }
                }
            };
            ws.send(JSON.stringify(msg));
            addMessage('sent', JSON.stringify(msg, null, 2), 'sent');
        }

        function getMessageTemplate(type) {
            const templates = {
                ping: {
                    type: 'ping',
                    timestamp: new Date().toISOString()
                },
                goal_update: {
                    type: 'goal_update',
                    data: {
                        goal_id: 'goal-456-def',
                        status: 'in_progress',
                        progress_percentage: 75.0
                    }
                },
                task_update: {
                    type: 'task_update',
                    data: {
                        task_id: 'task-111-aaa',
                        status: 'in_progress',
                        actual_hours: 5.5
                    }
                },
                code_validation: {
                    type: 'code_validation_request',
                    data: {
                        snapshot_id: 'snapshot-333-ccc',
                        language: 'python',
                        file_path: 'app/api/auth.py'
                    }
                }
            };
            return templates[type] || {};
        }

        function addMessage(type, content, className) {
            const timestamp = new Date().toLocaleTimeString();
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${className}`;
            messageDiv.innerHTML = `
                <div class="timestamp">[${timestamp}] ${type.toUpperCase()}</div>
                <pre style="margin: 5px 0 0 0; white-space: pre-wrap;">${content}</pre>
            `;
            messagesEl.appendChild(messageDiv);
            messagesEl.scrollTop = messagesEl.scrollHeight;
        }

        function clearMessages() {
            messagesEl.innerHTML = '';
        }

        // Auto-connect on load (optional)
        // window.onload = connect;
    </script>
</body>
</html>
```

### Uso del Test WebSocket:

1. **Abrir en navegador**:
```bash
open test_websocket.html
# O arrastra el archivo al navegador
```

2. **Conectar al servidor**:
   - Click en "Connect"
   - El status cambiará a "Connected"

3. **Enviar mensajes**:
   - Usa los botones "Quick Actions" para enviar mensajes predefinidos
   - O selecciona el tipo de mensaje y click "Send Message"

4. **Ver respuestas**:
   - Las respuestas del servidor aparecen en la sección "Messages"
   - Mensajes enviados en azul, recibidos en verde

---

## 📊 Flujo de Prueba Completo

### Escenario: Crear un curso y completar un goal

```bash
# 1. Crear usuario
curl -X POST "${API_URL}/users" \
  -H "Content-Type: application/json" \
  -d '{"email": "bob@example.com", "username": "bob", "full_name": "Bob Smith", "password": "pass123"}'
# Guarda el user_id de la respuesta

# 2. Crear curso
curl -X POST "${API_URL}/courses" \
  -H "Content-Type: application/json" \
  -d '{"title": "FastAPI Mastery", "description": "Master FastAPI development"}'
# Guarda el course_id

# 3. Publicar curso
curl -X POST "${API_URL}/courses/${COURSE_ID}/publish" \
  -H "Content-Type: application/json"

# 4. Crear goal
curl -X POST "${API_URL}/goals" \
  -H "Content-Type: application/json" \
  -d '{"course_id": "'${COURSE_ID}'", "title": "Build Auth System", "description": "Implement JWT authentication", "priority": "high"}'
# Guarda el goal_id

# 5. Crear task
curl -X POST "${API_URL}/tasks" \
  -H "Content-Type: application/json" \
  -d '{"goal_id": "'${GOAL_ID}'", "title": "Implement login endpoint", "description": "Create /login endpoint with JWT", "task_type": "code"}'
# Guarda el task_id

# 6. Iniciar task
curl -X PUT "${API_URL}/tasks/${TASK_ID}" \
  -H "Content-Type: application/json" \
  -d '{"status": "in_progress"}'

# 7. Crear código snapshot
curl -X POST "${API_URL}/code-snapshots" \
  -H "Content-Type: application/json" \
  -d '{"task_id": "'${TASK_ID}'", "file_path": "auth.py", "language": "python", "code_content": "def login(): pass"}'
# Guarda el snapshot_id

# 8. Validar código
curl -X PATCH "${API_URL}/code-snapshots/${SNAPSHOT_ID}/validation" \
  -H "Content-Type: application/json" \
  -d '{"validation_passed": true, "validation_score": 0.9, "validation_feedback": "Good code!"}'

# 9. Completar task
curl -X PUT "${API_URL}/tasks/${TASK_ID}" \
  -H "Content-Type: application/json" \
  -d '{"status": "completed"}'

# 10. Actualizar progreso del goal
curl -X PATCH "${API_URL}/goals/${GOAL_ID}/progress?progress_percentage=100" \
  -H "Content-Type: application/json"

# 11. Ver historial de eventos del goal
curl -X GET "${API_URL}/events/entities/goal/${GOAL_ID}/history" \
  -H "Content-Type: application/json"
```

---

## ✅ Checklist de Tests

- [ ] Users API
  - [ ] Crear usuario
  - [ ] Obtener usuario
  - [ ] Actualizar usuario
  - [ ] Desactivar usuario
- [ ] Courses API
  - [ ] Crear curso
  - [ ] Obtener curso
  - [ ] Listar cursos
  - [ ] Publicar curso
  - [ ] Archivar curso
- [ ] Goals API
  - [ ] Crear goal
  - [ ] Obtener goal
  - [ ] Listar goals (filtros)
  - [ ] Actualizar goal
  - [ ] Actualizar progreso
  - [ ] Completar goal
  - [ ] Eliminar goal
- [ ] Tasks API
  - [ ] Crear task
  - [ ] Obtener task
  - [ ] Listar tasks (filtros)
  - [ ] Actualizar task
  - [ ] Completar task
  - [ ] Eliminar task
- [ ] Code Snapshots API
  - [ ] Crear snapshot
  - [ ] Obtener snapshot
  - [ ] Listar snapshots (filtros)
  - [ ] Actualizar validación
  - [ ] Obtener último snapshot
  - [ ] Eliminar snapshot
- [ ] Events API
  - [ ] Crear event
  - [ ] Obtener event
  - [ ] Listar events (filtros)
  - [ ] Historial de entidad
  - [ ] Replay events
- [ ] WebSocket
  - [ ] Conectar
  - [ ] Enviar mensajes
  - [ ] Recibir respuestas
  - [ ] Desconectar

---

**Versión**: 1.0
**Fecha**: 2025-12-28
**Total Endpoints**: 40+
**Estado**: ✅ Listo para testing
