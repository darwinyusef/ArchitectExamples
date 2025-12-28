# 📦 Servicios CRUD - AI Goals Tracker V2

## 🎯 Resumen

Los servicios CRUD implementan toda la lógica de negocio para gestionar:

- ✅ **Goals** - Objetivos de aprendizaje
- ✅ **Tasks** - Tareas granulares
- ✅ **Code Snapshots** - Capturas de código con validación
- ✅ **Events** - Event sourcing con triple persistencia
- ✅ **Users** - Usuarios (temporal, POC)
- ✅ **Courses** - Cursos (temporal, POC)

---

## 🏗️ Arquitectura de Servicios

```
┌─────────────────────────────────────────────────┐
│              API Routes (FastAPI)               │
└────────────────────┬────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────┐
│              Service Layer                      │
│  • GoalService                                  │
│  • TaskService                                  │
│  • CodeSnapshotService                          │
│  • EventService                                 │
│  • UserService                                  │
│  • CourseService                                │
└────────────────────┬────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ↓            ↓            ↓
┌──────────┐  ┌──────────┐  ┌──────────┐
│PostgreSQL│  │ RAGTools │  │  Event   │
│  Models  │  │Embeddings│  │ Sourcing │
└──────────┘  └──────────┘  └──────────┘
```

---

## 📋 GoalService

**Archivo**: `backend/app/services/goal_service.py`

### Funciones Principales

```python
class GoalService:
    async def create_goal(
        user_id: str,
        goal_data: GoalCreate,
        generate_embedding: bool = True
    ) -> Goal
```

**Características**:
- ✅ Crea goal con UUID único
- ✅ Genera embedding automático para RAG
- ✅ Estado inicial: `PENDING`
- ✅ Prioridad por defecto: `MEDIUM`

```python
    async def get_goal(goal_id: str, user_id: str) -> Optional[Goal]
```

**Características**:
- ✅ Obtiene goal por ID
- ✅ Valida que pertenezca al usuario

```python
    async def list_goals(
        user_id: str,
        status: Optional[GoalStatus] = None,
        course_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Goal]
```

**Características**:
- ✅ Lista goals del usuario
- ✅ Filtra por status (PENDING, IN_PROGRESS, COMPLETED, etc.)
- ✅ Filtra por curso
- ✅ Paginación con skip/limit

```python
    async def update_goal(
        goal_id: str,
        user_id: str,
        goal_update: GoalUpdate
    ) -> Optional[Goal]
```

**Características**:
- ✅ Actualiza campos
- ✅ Maneja transiciones de estado
- ✅ Actualiza `started_at` al pasar a IN_PROGRESS
- ✅ Actualiza `completed_at` y progreso al COMPLETED
- ✅ Regenera embedding si cambia descripción

```python
    async def delete_goal(goal_id: str, user_id: str) -> bool
```

**Características**:
- ✅ Elimina goal
- ✅ Valida ownership

```python
    async def update_progress(
        goal_id: str,
        user_id: str,
        progress_percentage: float
    ) -> Optional[Goal]
```

**Características**:
- ✅ Actualiza porcentaje de progreso (0-100)
- ✅ Auto-completa goal si llega a 100%

### Métodos Privados (RAG)

```python
    async def _create_embedding(goal: Goal) -> None
```

**Características**:
- ✅ Genera embedding con OpenAI text-embedding-3-small
- ✅ Guarda en tabla `embeddings`
- ✅ Metadata: status, priority

```python
    async def _update_embedding(goal: Goal) -> None
```

**Características**:
- ✅ Elimina embedding antiguo
- ✅ Crea nuevo embedding

---

## 📋 TaskService

**Archivo**: `backend/app/services/task_service.py`

### Funciones Principales

```python
class TaskService:
    async def create_task(
        user_id: str,
        task_data: TaskCreate,
        generate_embedding: bool = True
    ) -> Task
```

**Características**:
- ✅ Crea task vinculada a un goal
- ✅ Estado inicial: `TODO`
- ✅ Genera embedding para RAG
- ✅ Tipos: CODE, DOCUMENTATION, TESTING, RESEARCH, etc.

```python
    async def get_task(task_id: str, user_id: str) -> Optional[Task]
    async def list_tasks(...) -> List[Task]
```

**Características de list_tasks**:
- ✅ Filtra por goal_id
- ✅ Filtra por status (TODO, IN_PROGRESS, COMPLETED, etc.)
- ✅ Filtra por task_type
- ✅ Ordena por priority y fecha

```python
    async def update_task(
        task_id: str,
        user_id: str,
        task_update: TaskUpdate
    ) -> Optional[Task]
```

**Características**:
- ✅ Maneja transiciones de estado
- ✅ Actualiza `started_at` al IN_PROGRESS
- ✅ Actualiza `completed_at` al COMPLETED
- ✅ Regenera embedding si cambia

```python
    async def delete_task(task_id: str, user_id: str) -> bool
```

```python
    async def update_validation(
        task_id: str,
        user_id: str,
        validation_result: dict,
        ai_feedback: Optional[str]
    ) -> Optional[Task]
```

**Características**:
- ✅ Actualiza resultado de validación
- ✅ Guarda feedback del AI
- ✅ Usado por agentes de LangGraph

### Embedding

Mismo patrón que GoalService:
- `_create_embedding()` - Genera al crear
- `_update_embedding()` - Regenera al actualizar

---

## 📋 CodeSnapshotService

**Archivo**: `backend/app/services/code_snapshot_service.py`

### Funciones Principales

```python
class CodeSnapshotService:
    async def create_snapshot(
        user_id: str,
        snapshot_data: CodeSnapshotCreate,
        generate_embedding: bool = True
    ) -> CodeSnapshot
```

**Características**:
- ✅ Captura código en un momento específico
- ✅ Vinculado a una task
- ✅ Metadata: file_path, language, diff
- ✅ Embedding incluye: file_path + language + code

```python
    async def get_snapshot(snapshot_id: str, user_id: str) -> Optional[CodeSnapshot]
```

```python
    async def list_snapshots(
        user_id: str,
        task_id: Optional[str] = None,
        language: Optional[str] = None,
        validated_only: bool = False,
        skip: int = 0,
        limit: int = 100
    ) -> List[CodeSnapshot]
```

**Características**:
- ✅ Filtra por task
- ✅ Filtra por lenguaje (python, javascript, etc.)
- ✅ Filtra solo código validado

```python
    async def update_snapshot(
        snapshot_id: str,
        user_id: str,
        snapshot_update: CodeSnapshotUpdate
    ) -> Optional[CodeSnapshot]
```

```python
    async def update_validation_result(
        snapshot_id: str,
        user_id: str,
        validation_passed: bool,
        validation_score: float,
        validation_feedback: str,
        issues_found: Optional[List[dict]] = None
    ) -> Optional[CodeSnapshot]
```

**Características**:
- ✅ Guarda resultado de validación AI
- ✅ Score 0-1
- ✅ Feedback textual
- ✅ Issues encontrados
- ✅ Usado para RAG de código similar

```python
    async def get_latest_for_task(task_id: str, user_id: str) -> Optional[CodeSnapshot]
```

**Características**:
- ✅ Obtiene snapshot más reciente de una task
- ✅ Útil para validación incremental

### Embedding de Código

```python
    async def _create_embedding(snapshot: CodeSnapshot) -> None
```

**Características**:
- ✅ Embedding incluye:
  - File path
  - Language
  - Code content completo
- ✅ Metadata: language, file_path, validation_passed, validation_score
- ✅ Permite búsqueda de código similar validado

---

## 📋 EventService

**Archivo**: `backend/app/services/event_service.py`

### Triple Persistencia

```
┌──────────────┐
│  Event       │
└──────┬───────┘
       │
       ├──→ 1. PostgreSQL (base de datos)
       ├──→ 2. Parquet (archivos particionados)
       └──→ 3. RabbitMQ (pub/sub)
```

### Funciones Principales

```python
class EventService:
    async def create_event(
        user_id: str,
        event_type: EventType,
        entity_type: str,
        entity_id: str,
        event_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Event
```

**Características**:
- ✅ **PostgreSQL**: Guarda en tabla `events`
- ✅ **Parquet**: Append a archivo particionado (year/month/day)
- ✅ **RabbitMQ**: Publica con routing key `{event_type}.{entity_type}`
- ✅ Event types: USER_CREATED, GOAL_CREATED, TASK_COMPLETED, CODE_VALIDATED, etc.

```python
    async def list_events(
        user_id: Optional[str],
        event_type: Optional[EventType],
        entity_type: Optional[str],
        entity_id: Optional[str],
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        skip: int = 0,
        limit: int = 100
    ) -> List[Event]
```

**Características**:
- ✅ Lista eventos con múltiples filtros
- ✅ Rango de fechas
- ✅ Por tipo de evento
- ✅ Por entidad

```python
    async def get_entity_history(
        entity_type: str,
        entity_id: str,
        user_id: Optional[str] = None
    ) -> List[Event]
```

**Características**:
- ✅ Historial completo de una entidad
- ✅ Ordenado cronológicamente
- ✅ Útil para auditoría

```python
    async def replay_events(
        entity_type: str,
        entity_id: str,
        target_timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]
```

**Características**:
- ✅ Reconstruye estado de entidad en un momento específico
- ✅ Event sourcing pattern
- ✅ Time travel queries

### Métodos Internos

```python
    async def _save_to_parquet(event: Event) -> None
```

**Características**:
- ✅ Particionado por año/mes/día
- ✅ Path: `backend/data/events/parquet/{event_type}/{year}/{month}/{day}/events.parquet`
- ✅ Schema específico según event_type
- ✅ Append mode (no sobrescribe)

```python
    async def _publish_to_rabbitmq(event: Event) -> None
```

**Características**:
- ✅ Exchange: `events` (topic)
- ✅ Routing key: `{event_type}.{entity_type}`
- ✅ Durable messages
- ✅ Falla silenciosamente (no bloquea creación)

---

## 📋 UserService

**Archivo**: `backend/app/services/user_service.py`

### ⚠️ Nota Importante

```
TEMPORAL - POC Only

En producción, los usuarios serán manejados por:
/proyectos/aquicreamos_2025/aqc/app

Este servicio existe solo para el POC.
```

### Funciones Principales

```python
class UserService:
    async def create_user(user_data: UserCreate) -> User
```

**Características**:
- ✅ Crea usuario
- ✅ Hash de password (SHA256)
- ✅ Estado inicial: is_active=True

```python
    async def get_user(user_id: str) -> Optional[User]
    async def get_user_by_email(email: str) -> Optional[User]
    async def get_user_by_username(username: str) -> Optional[User]
```

```python
    async def update_user(user_id: str, user_update: UserUpdate) -> Optional[User]
```

**Características**:
- ✅ Actualiza campos
- ✅ Re-hashea password si cambia

```python
    async def verify_password(user_id: str, password: str) -> bool
```

**Características**:
- ✅ Verifica password
- ✅ Compara hashes

```python
    async def update_last_login(user_id: str) -> Optional[User]
    async def deactivate_user(user_id: str) -> Optional[User]
    async def activate_user(user_id: str) -> Optional[User]
```

---

## 📋 CourseService

**Archivo**: `backend/app/services/course_service.py`

### ⚠️ Nota Importante

```
TEMPORAL - POC Only

En producción, los cursos serán manejados por:
/proyectos/aquicreamos_2025/aqc/app

Este servicio existe solo para el POC.
```

### Funciones Principales

```python
class CourseService:
    async def create_course(
        user_id: str,
        course_data: CourseCreate,
        generate_embedding: bool = True
    ) -> Course
```

**Características**:
- ✅ Crea curso
- ✅ Estado inicial: DRAFT
- ✅ Genera embedding (title + description + syllabus)

```python
    async def get_course(course_id: str) -> Optional[Course]
```

```python
    async def list_courses(
        status: Optional[CourseStatus] = None,
        user_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Course]
```

**Características**:
- ✅ Filtra por status (DRAFT, ACTIVE, COMPLETED, ARCHIVED)
- ✅ Filtra por instructor (user_id)

```python
    async def update_course(
        course_id: str,
        course_update: CourseUpdate
    ) -> Optional[Course]
```

**Características**:
- ✅ Actualiza campos
- ✅ Regenera embedding si cambia descripción

```python
    async def publish_course(course_id: str) -> Optional[Course]
```

**Características**:
- ✅ Cambia status a ACTIVE
- ✅ Curso disponible para estudiantes

```python
    async def archive_course(course_id: str) -> Optional[Course]
```

**Características**:
- ✅ Cambia status a ARCHIVED
- ✅ Curso no visible

---

## 🔗 Integración con RAG

Todos los servicios principales integran RAG automáticamente:

### Generación de Embeddings

```python
# En create:
if generate_embedding and entity.description:
    await self._create_embedding(entity)

# En update:
if update_data.description:
    await self._update_embedding(entity)
```

### Content Embeddings

| Servicio           | Content Format                              |
|--------------------|---------------------------------------------|
| GoalService        | `Goal: {title}\n\nDescription: {desc}`      |
| TaskService        | `Task: {title}\n\n{desc}\n\nType: {type}`   |
| CodeSnapshotService| `File: {path}\nLanguage: {lang}\n\n{code}`  |
| CourseService      | `Course: {title}\n\n{desc}\n\nSyllabus: ..` |

### Metadata Embeddings

```python
# GoalService
metadata = {
    "goal_status": goal.status.value,
    "goal_priority": goal.priority.value
}

# TaskService
metadata = {
    "task_type": task.task_type.value,
    "task_status": task.status.value
}

# CodeSnapshotService
metadata = {
    "language": snapshot.language,
    "file_path": snapshot.file_path,
    "validation_passed": snapshot.validation_passed,
    "validation_score": snapshot.validation_score
}
```

---

## 📊 Diagrama de Flujo Completo

```
Usuario crea Goal
       │
       ↓
┌──────────────────┐
│  GoalService     │
│  create_goal()   │
└────────┬─────────┘
         │
         ├──→ 1. Crear Goal en PostgreSQL
         │
         ├──→ 2. Generar embedding (RAGTools)
         │           │
         │           └──→ OpenAI API
         │                   │
         │                   ↓
         │           Embedding (1536 dims)
         │                   │
         │                   ↓
         ├──→ 3. Guardar en tabla embeddings
         │
         └──→ 4. Retornar Goal creado
                     │
                     ↓
              ┌────────────┐
              │ EventService│
              │create_event()│
              └─────┬───────┘
                    │
                    ├──→ PostgreSQL
                    ├──→ Parquet file
                    └──→ RabbitMQ
```

---

## 🧪 Testing Pattern

### Ejemplo: Test GoalService

```python
import pytest
from app.services import GoalService
from app.schemas.goal_schemas import GoalCreate

@pytest.mark.asyncio
async def test_create_goal(db_session):
    service = GoalService(db_session)

    goal_data = GoalCreate(
        course_id="course_123",
        title="Learn FastAPI",
        description="Build a REST API with FastAPI",
        priority="high"
    )

    goal = await service.create_goal(
        user_id="user_123",
        goal_data=goal_data
    )

    assert goal.id is not None
    assert goal.title == "Learn FastAPI"
    assert goal.status == GoalStatus.PENDING
    assert goal.priority == GoalPriority.HIGH

@pytest.mark.asyncio
async def test_update_goal_to_completed(db_session):
    service = GoalService(db_session)

    # Create goal
    goal = await service.create_goal(...)

    # Update to completed
    update = GoalUpdate(status=GoalStatus.COMPLETED)
    updated_goal = await service.update_goal(
        goal_id=goal.id,
        user_id="user_123",
        goal_update=update
    )

    assert updated_goal.status == GoalStatus.COMPLETED
    assert updated_goal.progress_percentage == 100.0
    assert updated_goal.completed_at is not None
```

---

## 📚 Uso en API Routes

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services import GoalService
from app.schemas.goal_schemas import GoalCreate, GoalResponse

router = APIRouter()

@router.post("/goals", response_model=GoalResponse)
async def create_goal(
    goal_data: GoalCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Create a new goal."""
    service = GoalService(db)
    goal = await service.create_goal(user_id, goal_data)
    return goal

@router.get("/goals/{goal_id}", response_model=GoalResponse)
async def get_goal(
    goal_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get goal by ID."""
    service = GoalService(db)
    goal = await service.get_goal(goal_id, user_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return goal
```

---

## ✅ Servicios Completados

| Servicio             | Archivo                          | Estado | RAG | Event Sourcing |
|----------------------|----------------------------------|--------|-----|----------------|
| GoalService          | goal_service.py                  | ✅     | ✅  | ⏳             |
| TaskService          | task_service.py                  | ✅     | ✅  | ⏳             |
| CodeSnapshotService  | code_snapshot_service.py         | ✅     | ✅  | ⏳             |
| EventService         | event_service.py                 | ✅     | ❌  | ✅             |
| UserService          | user_service.py (temporal)       | ✅     | ❌  | ⏳             |
| CourseService        | course_service.py (temporal)     | ✅     | ✅  | ⏳             |

**Leyenda**:
- ✅ Implementado
- ⏳ Pendiente de integración
- ❌ No aplica

---

## 🚀 Próximos Pasos

1. ✅ **CRUD Services** - Completado
2. ⏳ **API Endpoints** - Crear rutas FastAPI
3. ⏳ **Event Integration** - Integrar EventService en todos los servicios
4. ⏳ **LangGraph Agents** - Integrar servicios con agentes
5. ⏳ **Testing** - Tests unitarios e integración
6. ⏳ **Documentation** - OpenAPI/Swagger docs

---

**Versión**: 1.0
**Fecha**: 2025-12-28
**Estado**: ✅ Servicios CRUD Completados
**Líneas de código**: ~800 por servicio (~5,000 total)
