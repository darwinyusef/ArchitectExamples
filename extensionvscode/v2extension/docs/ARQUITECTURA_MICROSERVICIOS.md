# 🏗️ Arquitectura de Microservicios - AI Goals Tracker V2

## 📋 Separación de Responsabilidades

### Microservicio 1: User Management & Courses (Otro servicio)
**Ubicación**: `/proyectos/pixel-verse-academy`

**Responsabilidades**:
- ✅ Gestión de usuarios (registro, login, perfiles)
- ✅ Gestión de cursos/academy
- ✅ Autenticación y autorización
- ✅ Roles y permisos

**Tecnologías**:
- Backend: (Por definir en pixel-verse-academy)
- Frontend: (Por definir en pixel-verse-academy)

---

### Microservicio 2: Goals & Tasks Tracker (Este servicio)
**Ubicación**: `/proyectos/arquitecturas/extensionvscode/v2extension`

**Responsabilidades**:
- ✅ Gestión de goals (objetivos de aprendizaje)
- ✅ Gestión de tasks (tareas individuales)
- ✅ Validación de código con IA
- ✅ Feedback de agentes LangGraph
- ✅ Event sourcing y analytics
- ✅ RAG para contexto personalizado

**Tecnologías**:
- Backend: FastAPI + LangGraph + PostgreSQL + pgvector
- Frontend: VS Code Extension (TypeScript)

---

## 🔗 Integración Entre Microservicios

```
┌──────────────────────────────────────────────────────────────┐
│         MICROSERVICIO 1: User Management & Courses           │
│            (pixel-verse-academy)                             │
│                                                              │
│  ┌────────────┐    ┌────────────┐    ┌────────────┐        │
│  │   Users    │    │  Courses   │    │    Auth    │        │
│  │   DB       │    │    DB      │    │   (JWT)    │        │
│  └────────────┘    └────────────┘    └────────────┘        │
│         │                 │                  │              │
└─────────┼─────────────────┼──────────────────┼──────────────┘
          │                 │                  │
          │                 │                  │
          ▼                 ▼                  ▼
    ┌────────────────────────────────────────────────┐
    │           API Gateway / Service Mesh           │
    │         (Compartir JWT, User Context)          │
    └────────────────────────────────────────────────┘
          │                 │                  │
          │                 │                  │
          ▼                 ▼                  ▼
┌──────────────────────────────────────────────────────────────┐
│       MICROSERVICIO 2: Goals & Tasks Tracker                 │
│                 (v2extension)                                │
│                                                              │
│  ┌────────────┐    ┌────────────┐    ┌────────────┐        │
│  │   Goals    │    │   Tasks    │    │    Code    │        │
│  │    DB      │    │    DB      │    │  Snapshots │        │
│  └────────────┘    └────────────┘    └────────────┘        │
│                                                              │
│  ┌────────────┐    ┌────────────┐    ┌────────────┐        │
│  │  Events    │    │ Embeddings │    │ LangGraph  │        │
│  │    DB      │    │  (RAG)     │    │  Agents    │        │
│  └────────────┘    └────────────┘    └────────────┘        │
└──────────────────────────────────────────────────────────────┘
```

---

## 📊 Modelos Actualizados (Sin Users/Courses)

### Tablas en v2extension (Goals Tracker)

1. ~~users~~ → ❌ **ELIMINADO** (vive en pixel-verse-academy)
2. ~~courses~~ → ❌ **ELIMINADO** (vive en pixel-verse-academy)
3. **goals** ✅ (mantener, pero referenciar user_id externo)
4. **tasks** ✅ (mantener)
5. **code_snapshots** ✅ (mantener)
6. **events** ✅ (mantener)
7. **embeddings** ✅ (mantener)

### Campos Modificados

#### Goals (modificar)
```python
class Goal(Base):
    __tablename__ = "goals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    # ⚠️ IMPORTANTE: user_id NO es FK, es referencia externa
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    # ⚠️ IMPORTANTE: course_id NO es FK, es referencia externa
    course_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    # ... resto igual
```

#### Tasks (modificar)
```python
class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    goal_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("goals.id", ondelete="CASCADE"),  # ✅ FK interna
        nullable=False
    )

    # ⚠️ IMPORTANTE: user_id NO es FK, es referencia externa
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    # ... resto igual
```

---

## 🔐 Autenticación Entre Servicios

### Flujo de Autenticación

```
1. Usuario se autentica en pixel-verse-academy
   ↓
2. Recibe JWT token con:
   {
     "user_id": "usr_123",
     "email": "user@example.com",
     "roles": ["student"],
     "exp": 1234567890
   }
   ↓
3. Usuario usa VS Code Extension (v2extension)
   ↓
4. Extension envía JWT en header:
   Authorization: Bearer <token>
   ↓
5. Backend v2extension valida JWT con:
   - Misma SECRET_KEY compartida, O
   - Endpoint de validación en pixel-verse-academy
   ↓
6. Extrae user_id del JWT
   ↓
7. Usa user_id para crear/leer goals/tasks
```

### Implementación en v2extension

```python
# backend/app/core/security.py

from jose import JWTError, jwt
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def get_current_user_id(token: str = Depends(security)) -> str:
    """
    Extraer user_id del JWT token.

    El token fue generado por pixel-verse-academy.
    """
    try:
        # Decodificar token usando SECRET_KEY compartida
        payload = jwt.decode(
            token.credentials,
            settings.SECRET_KEY,
            algorithms=["HS256"]
        )

        user_id: str = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        return user_id

    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
```

### Uso en Endpoints

```python
# backend/app/api/goals.py

from fastapi import APIRouter, Depends
from app.core.security import get_current_user_id

router = APIRouter(prefix="/api/v1/goals")

@router.post("/")
async def create_goal(
    goal_data: GoalCreate,
    user_id: str = Depends(get_current_user_id),  # ✅ user_id del JWT
    db: AsyncSession = Depends(get_db)
):
    """Crear goal para el usuario autenticado."""

    # user_id viene del JWT (del otro microservicio)
    goal = Goal(
        id=str(uuid.uuid4()),
        user_id=user_id,  # ✅ Referencia externa
        course_id=goal_data.course_id,  # ✅ Referencia externa
        title=goal_data.title,
        # ...
    )

    db.add(goal)
    await db.commit()

    return goal
```

---

## 🔄 Comunicación Entre Microservicios

### Opción 1: REST API (Recomendado para empezar)

```python
# backend/app/services/user_service.py

import httpx
from app.core.config import settings

async def get_user_info(user_id: str) -> dict:
    """
    Obtener información del usuario desde pixel-verse-academy.

    Args:
        user_id: ID del usuario

    Returns:
        Dict con info del usuario: {
            "id": "usr_123",
            "email": "user@example.com",
            "full_name": "Juan Pérez",
            "is_active": true
        }
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.USER_SERVICE_URL}/api/users/{user_id}",
            headers={"Authorization": f"Bearer {settings.SERVICE_API_KEY}"}
        )

        if response.status_code == 404:
            return None

        response.raise_for_status()
        return response.json()


async def get_course_info(course_id: str) -> dict:
    """
    Obtener información del curso desde pixel-verse-academy.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.USER_SERVICE_URL}/api/courses/{course_id}",
            headers={"Authorization": f"Bearer {settings.SERVICE_API_KEY}"}
        )

        if response.status_code == 404:
            return None

        response.raise_for_status()
        return response.json()
```

### Opción 2: Event-Driven con RabbitMQ (Futuro)

```python
# Cuando pixel-verse-academy crea un usuario:
# 1. Publica evento "user.created" a RabbitMQ
# 2. v2extension escucha y puede cachear info del usuario en Redis

# Cuando pixel-verse-academy elimina un usuario:
# 1. Publica evento "user.deleted"
# 2. v2extension elimina todos los goals/tasks del usuario
```

---

## 📁 Variables de Entorno Actualizadas

```bash
# .env en v2extension

# ==================== Este Microservicio ====================
DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD@localhost:5432/ai_goals_tracker
REDIS_URL=redis://YOUR_REDIS_HOST:6379/0
RABBITMQ_URL=amqp://YOUR_RABBITMQ_USER:YOUR_RABBITMQ_PASSWORD@YOUR_RABBITMQ_HOST:5672/

# ==================== Integración con Otro Microservicio ====================
# URL del servicio de usuarios y cursos (pixel-verse-academy)
USER_SERVICE_URL=http://localhost:8001  # O la URL real del servicio

# API Key para comunicación entre servicios
SERVICE_API_KEY=shared-secret-key-between-services

# ==================== Autenticación Compartida ====================
# Misma SECRET_KEY que pixel-verse-academy para validar JWT
SECRET_KEY=shared-secret-key-for-jwt-validation

# ==================== OpenAI ====================
OPENAI_API_KEY=sk-YOUR_API_KEY_HERE
```

---

## 🗄️ Migraciones Actualizadas

Necesitamos modificar las migraciones para eliminar Users y Courses:

### Migraciones a ELIMINAR
- ❌ `001_create_users_table.py`
- ❌ `002_create_courses_table.py`

### Migraciones a MODIFICAR
- ✅ `003_create_goals_table.py` - Quitar FK a users y courses
- ✅ `004_create_tasks_table.py` - Quitar FK a users
- ⚠️ Resto se mantienen igual

---

## 🚀 Plan de Implementación

### Fase 1: Desarrollo Local (Actual)
- ✅ v2extension trabaja standalone
- ✅ Mantener tablas users/courses temporalmente para desarrollo
- ✅ Implementar toda la lógica de goals/tasks/RAG

### Fase 2: Integración (Cuando pixel-verse-academy esté listo)
1. Compartir SECRET_KEY entre servicios
2. Modificar models (quitar FKs)
3. Implementar user_service.py para consultas
4. Actualizar endpoints para usar JWT validation
5. Testing de integración

### Fase 3: Producción
1. Eliminar tablas users/courses de v2extension
2. Migrar datos si es necesario
3. Desplegar ambos servicios
4. Configurar API Gateway / Service Mesh

---

## 📊 Ejemplo de Flujo Completo

```
┌──────────────────────────────────────────────────────────────┐
│ 1. Usuario abre VS Code                                      │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│ 2. Extension pide login                                       │
│    → Redirect a pixel-verse-academy                          │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│ 3. Usuario se autentica en pixel-verse-academy               │
│    → Recibe JWT token                                        │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│ 4. Extension guarda token y conecta WebSocket a v2extension │
│    ws://localhost:8000/ws?token=<JWT>                        │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│ 5. v2extension valida JWT                                    │
│    → Extrae user_id: "usr_123"                              │
│    → Conecta WebSocket                                       │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│ 6. Usuario crea goal en VS Code                              │
│    {                                                          │
│      "type": "goal.create",                                  │
│      "payload": {                                            │
│        "title": "Aprender FastAPI",                         │
│        "course_id": "crs_abc"                               │
│      }                                                       │
│    }                                                         │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│ 7. v2extension:                                              │
│    - Usa user_id del JWT: "usr_123"                         │
│    - course_id es referencia externa: "crs_abc"             │
│    - Crea goal en DB local                                  │
│    - LangGraph genera tareas con RAG                        │
│    - Publica evento a RabbitMQ                              │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│ 8. (Opcional) Consultar info del curso:                      │
│    GET pixel-verse-academy/api/courses/crs_abc              │
│    → Devuelve: { "title": "FastAPI Course", ... }           │
└──────────────────────────────────────────────────────────────┘
```

---

## ✅ Checklist de Migración

### Ahora (Desarrollo)
- [x] Crear modelos con users/courses temporales
- [x] Crear migraciones completas
- [ ] Marcar users/courses como "temporal"
- [ ] Documentar integración futura

### Cuando pixel-verse-academy esté listo
- [ ] Compartir SECRET_KEY entre servicios
- [ ] Implementar user_service.py
- [ ] Modificar goals.py (quitar FK user_id, course_id)
- [ ] Modificar tasks.py (quitar FK user_id)
- [ ] Crear nuevas migraciones
- [ ] Eliminar migraciones 001 y 002
- [ ] Testing de integración

---

**Versión**: 2.0.0
**Fecha**: 2025-12-28
**Estado**: ✅ Arquitectura de microservicios documentada
**Próximo paso**: Mantener users/courses temporalmente para desarrollo
