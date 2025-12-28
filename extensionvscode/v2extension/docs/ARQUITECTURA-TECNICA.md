# Arquitectura Técnica - AI Goals Tracker V2

## Stack Tecnológico

### Backend
- **Framework**: FastAPI + Uvicorn (ASGI)
- **Orquestación IA**: LangGraph + LangChain
- **LLM**: OpenAI GPT-4
- **MCP**: FastMCP para tools integration
- **WebSockets**: FastAPI WebSocket + asyncio
- **Message Broker**: RabbitMQ (aio-pika)
- **Base de Datos**: PostgreSQL 15+ con pgvector
- **Cache/State**: Redis 7+
- **Storage**: MinIO (S3-compatible)
- **Autenticación**: JWT (PyJWT)
- **Containerización**: Docker + Docker Compose
- **CI/CD**: Jenkins

### Frontend (VS Code Extension)
- **Runtime**: Node.js 18+
- **Lenguaje**: TypeScript 5+
- **Framework**: VS Code Extension API
- **WebSocket Client**: ws library
- **HTTP Client**: axios
- **State Management**: Custom + LocalStorage
- **UI Components**: Webview API + Tailwind CSS

### Infraestructura
- **Formato de Eventos**: Apache Parquet
- **Data Lake**: MinIO buckets
- **Monitoreo**: Prometheus + Grafana (futuro)
- **Logs**: Structured logging (JSON)

---

## Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                      VS Code Extension (Client)                  │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────────┐  │
│  │  UI Components │  │ WebSocket      │  │  State Manager   │  │
│  │  - TreeView    │──│ Client         │──│  - Goals         │  │
│  │  - Webviews    │  │ - Real-time    │  │  - Tasks         │  │
│  │  - Commands    │  │ - Reconnect    │  │  - User State    │  │
│  └────────────────┘  └────────────────┘  └──────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │ WSS (WebSocket Secure)
                             │ + JWT Authentication
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Server (Backend)                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              WebSocket Handler Layer                      │  │
│  │  - Connection Manager                                     │  │
│  │  - Auth Middleware                                        │  │
│  │  - Message Router                                         │  │
│  └────────────────────────┬─────────────────────────────────┘  │
│                           │                                     │
│  ┌────────────────────────▼─────────────────────────────────┐  │
│  │                 LangGraph Orchestrator                    │  │
│  │  ┌──────────────────────────────────────────────────┐    │  │
│  │  │           State Machine (Redis)                  │    │  │
│  │  └──────────────────────────────────────────────────┘    │  │
│  │                                                           │  │
│  │  ┌──────────────────────────────────────────────────┐    │  │
│  │  │    Nodo 1: Autenticación & Autorización         │    │  │
│  │  │    - Validar JWT                                 │    │  │
│  │  │    - Verificar acceso a cursos                   │    │  │
│  │  │    Tools: [validate_token, check_enrollment]     │    │  │
│  │  └──────────────────────────────────────────────────┘    │  │
│  │                                                           │  │
│  │  ┌──────────────────────────────────────────────────┐    │  │
│  │  │    Nodo 2: Goal Generator Agent                  │    │  │
│  │  │    - Crear retos de código personalizados       │    │  │
│  │  │    - Generar tasks secuenciales                  │    │  │
│  │  │    Tools: [create_goal, generate_tasks, ai_gen]  │    │  │
│  │  └──────────────────────────────────────────────────┘    │  │
│  │                                                           │  │
│  │  ┌──────────────────────────────────────────────────┐    │  │
│  │  │    Nodo 3: Course Manager Agent                  │    │  │
│  │  │    - Documentar retos en cursos                  │    │  │
│  │  │    - Estructurar contenido educativo             │    │  │
│  │  │    Tools: [create_course, add_lesson, vector_db] │    │  │
│  │  └──────────────────────────────────────────────────┘    │  │
│  │                                                           │  │
│  │  ┌──────────────────────────────────────────────────┐    │  │
│  │  │    Nodo 4: Feedback Agent (Continuous)           │    │  │
│  │  │    - Feedback corto en tiempo real               │    │  │
│  │  │    - Sugerencias durante coding                  │    │  │
│  │  │    Tools: [analyze_code, give_hint, validate]    │    │  │
│  │  └──────────────────────────────────────────────────┘    │  │
│  │                                                           │  │
│  │  ┌──────────────────────────────────────────────────┐    │  │
│  │  │    Nodo 5: Performance Evaluator Agent           │    │  │
│  │  │    - Evaluar desempeño del usuario               │    │  │
│  │  │    - Enviar eventos al data lake                 │    │  │
│  │  │    Tools: [evaluate_perf, emit_event, to_parquet]│    │  │
│  │  └──────────────────────────────────────────────────┘    │  │
│  │                                                           │  │
│  │  ┌──────────────────────────────────────────────────┐    │  │
│  │  │    Nodo 6: State Monitor Agent                   │    │  │
│  │  │    - Revisar estados fundamentales               │    │  │
│  │  │    - Cambiar flujos según necesidad              │    │  │
│  │  │    Tools: [check_state, update_flow, redis_ops]  │    │  │
│  │  └──────────────────────────────────────────────────┘    │  │
│  │                                                           │  │
│  │  ┌──────────────────────────────────────────────────┐    │  │
│  │  │    Nodo 7: Context Organizer Agent               │    │  │
│  │  │    - Entender necesidad global del usuario       │    │  │
│  │  │    - Priorizar tareas según contexto             │    │  │
│  │  │    Tools: [analyze_context, prioritize, search]  │    │  │
│  │  └──────────────────────────────────────────────────┘    │  │
│  │                                                           │  │
│  │  ┌──────────────────────────────────────────────────┐    │  │
│  │  │    Nodo 8: Emotional Support Agent               │    │  │
│  │  │    - Detectar estado emocional                   │    │  │
│  │  │    - Motivar constantemente                      │    │  │
│  │  │    Tools: [detect_mood, motivate, send_modal]    │    │  │
│  │  └──────────────────────────────────────────────────┘    │  │
│  │                                                           │  │
│  │  ┌──────────────────────────────────────────────────┐    │  │
│  │  │    Nodo 9: Contract Validator Agent              │    │  │
│  │  │    - Verificar condiciones de contrato           │    │  │
│  │  │    - Detectar cambios en términos                │    │  │
│  │  │    Tools: [check_contract, validate_terms]       │    │  │
│  │  └──────────────────────────────────────────────────┘    │  │
│  └───────────────────────────────────────────────────────────┘  │
│                           │                                     │
│  ┌────────────────────────▼─────────────────────────────────┐  │
│  │              Event Sourcing Layer                        │  │
│  │  - Emit events to RabbitMQ                               │  │
│  │  - Event types: goal_created, task_completed, etc.       │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                    ┌────────┴────────┐
                    │                 │
          ┌─────────▼────────┐  ┌────▼──────────┐
          │   RabbitMQ       │  │   PostgreSQL  │
          │   (Events)       │  │   + pgvector  │
          │   ┌──────────┐   │  │   - Users     │
          │   │ Exchanges│   │  │   - Courses   │
          │   │ Queues   │   │  │   - Goals     │
          │   │ Bindings │   │  │   - Events    │
          │   └──────────┘   │  │   - Embeddings│
          └──────────────────┘  └───────────────┘
                    │
          ┌─────────▼────────┐
          │   Event          │
          │   Processors     │
          │   ┌──────────┐   │
          │   │ To MinIO │───┼──────────┐
          │   │ Parquet  │   │          │
          │   └──────────┘   │    ┌─────▼──────┐
          └──────────────────┘    │   MinIO    │
                                  │ Data Lake  │
                    ┌─────────┐   │  (Parquet) │
                    │  Redis  │   └────────────┘
                    │ (State) │
                    └─────────┘
```

---

## Flujo de Comunicación en Tiempo Real

### 1. Conexión Inicial
```
Client (VS Code)                     Server (FastAPI)
      │                                    │
      │  1. WSS handshake + JWT            │
      ├────────────────────────────────────▶
      │                                    │
      │  2. Validate JWT (Nodo 1)          │
      │                                    ├─── Redis: check session
      │                                    │
      │  3. Connection established         │
      ◀────────────────────────────────────┤
      │     + session_id                   │
      │                                    │
      │  4. Subscribe to user events       │
      │                                    ├─── RabbitMQ: create queue
      │                                    │
```

### 2. Creación de Goal
```
Client                                 Server                        LangGraph
  │                                      │                              │
  │ create_goal_request                  │                              │
  ├──────────────────────────────────────▶                              │
  │                                      │  Trigger Nodo 2              │
  │                                      ├──────────────────────────────▶
  │                                      │                              │
  │                                      │  Generate tasks (AI)         │
  │                                      │◀─────────────────────────────┤
  │                                      │                              │
  │                                      │  Nodo 3: Document course     │
  │                                      ├──────────────────────────────▶
  │                                      │                              │
  │  goal_created event                  │                              │
  ◀──────────────────────────────────────┤                              │
  │                                      │  Emit event to RabbitMQ      │
  │                                      ├─────────┐                    │
  │                                      │         │                    │
  │                                      │  ┌──────▼──────┐             │
  │                                      │  │  RabbitMQ   │             │
  │                                      │  │  Publishers │             │
  │                                      │  └─────────────┘             │
```

### 3. Validación de Task (Tiempo Real)
```
Client                                 Server                    Nodo 4 (Feedback)
  │                                      │                              │
  │ validate_task_request                │                              │
  ├──────────────────────────────────────▶                              │
  │  + code snippet                      │  analyze_code()              │
  │                                      ├──────────────────────────────▶
  │                                      │                              │
  │                                      │  AI validation               │
  │                                      │◀─────────────────────────────┤
  │                                      │  + suggestions               │
  │  validation_result (streaming)       │                              │
  ◀──────────────────────────────────────┤                              │
  │  chunk 1: "Analyzing..."             │                              │
  ◀──────────────────────────────────────┤                              │
  │  chunk 2: "Found issue..."           │                              │
  ◀──────────────────────────────────────┤                              │
  │  chunk 3: "Suggestion: ..."          │                              │
  ◀──────────────────────────────────────┤                              │
```

### 4. Motivación Emocional (Push)
```
Nodo 8 (Emotional)                    Server                        Client
  │                                      │                              │
  │  detect_mood() triggers              │                              │
  │  motivation needed                   │                              │
  ├──────────────────────────────────────▶                              │
  │                                      │  motivation_modal event      │
  │                                      ├──────────────────────────────▶
  │                                      │                              │
  │                                      │                              │ Show modal
  │                                      │  user_response               │ in VS Code
  │                                      ◀──────────────────────────────┤
  │  process_response()                  │                              │
  ◀──────────────────────────────────────┤                              │
```

---

## Modelo de Datos

### PostgreSQL Schema

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Courses table
CREATE TABLE courses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User enrollments
CREATE TABLE enrollments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    course_id UUID REFERENCES courses(id),
    enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'active',
    UNIQUE(user_id, course_id)
);

-- Goals table
CREATE TABLE goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id UUID REFERENCES courses(id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    documentation TEXT, -- Markdown content
    difficulty VARCHAR(50), -- easy, medium, hard
    estimated_time INTEGER, -- minutes
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tasks table
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    goal_id UUID REFERENCES goals(id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    validation_criteria JSONB, -- AI validation rules
    order_index INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User progress
CREATE TABLE user_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    goal_id UUID REFERENCES goals(id),
    task_id UUID REFERENCES tasks(id) NULL,
    status VARCHAR(50), -- pending, in_progress, completed, failed
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    attempts INTEGER DEFAULT 0,
    code_snapshot TEXT, -- Last code submitted
    UNIQUE(user_id, goal_id, task_id)
);

-- Events table (Event Sourcing)
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type VARCHAR(100) NOT NULL,
    user_id UUID REFERENCES users(id),
    aggregate_id UUID, -- goal_id, task_id, etc.
    payload JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    parquet_path VARCHAR(500) -- MinIO path
);

-- Vector embeddings (pgvector)
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type VARCHAR(50), -- 'goal', 'course', 'task'
    entity_id UUID NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536), -- OpenAI ada-002 dimension
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ON embeddings USING ivfflat (embedding vector_cosine_ops);
```

### Redis Schema (State Machines)

```python
# User session state
user_session:{user_id} = {
    "connection_id": "ws_conn_123",
    "current_goal_id": "uuid",
    "current_task_id": "uuid",
    "mood_score": 0.8,  # Nodo 8
    "last_activity": "2025-12-28T00:00:00Z",
    "context": {
        "recent_errors": [...],
        "focus_areas": [...]
    }
}

# LangGraph state per goal execution
goal_state:{execution_id} = {
    "goal_id": "uuid",
    "user_id": "uuid",
    "current_node": "nodo_4_feedback",
    "state_data": {...},
    "history": [...]
}

# WebSocket connections
ws_connections:{connection_id} = {
    "user_id": "uuid",
    "connected_at": "timestamp",
    "ip": "127.0.0.1"
}
```

### RabbitMQ Event Types

```python
# Exchange: ai_goals_tracker
# Routing keys pattern: {entity}.{action}

events = [
    "user.registered",
    "user.logged_in",
    "user.logged_out",

    "goal.created",
    "goal.started",
    "goal.completed",
    "goal.failed",

    "task.started",
    "task.validated",
    "task.completed",
    "task.failed",

    "code.submitted",
    "code.validated",

    "feedback.generated",  # Nodo 4
    "performance.evaluated",  # Nodo 5
    "mood.detected",  # Nodo 8
    "motivation.sent",  # Nodo 8

    "contract.checked",  # Nodo 9
    "state.changed",  # Nodo 6
]
```

### MinIO Buckets Structure

```
ai-goals-tracker/
├── events/
│   ├── year=2025/
│   │   ├── month=12/
│   │   │   ├── day=28/
│   │   │   │   ├── events_000001.parquet
│   │   │   │   └── events_000002.parquet
├── code_snapshots/
│   ├── user_id={uuid}/
│   │   ├── goal_id={uuid}/
│   │   │   ├── snapshot_v1.py
│   │   │   └── snapshot_v2.py
├── analytics/
│   ├── daily_aggregates/
│   │   └── 2025-12-28.parquet
```

---

## Seguridad

### Autenticación
- JWT tokens con expiración (1h access, 7d refresh)
- Refresh token rotation
- Blacklist de tokens revocados (Redis)

### Autorización
- RBAC (Role-Based Access Control)
- Roles: student, instructor, admin
- Permisos por curso

### WebSocket Security
- JWT en handshake inicial
- Validación en cada mensaje
- Rate limiting por usuario
- Timeout de inactividad

### Data Protection
- Passwords con bcrypt (cost factor 12)
- Secrets en variables de entorno (.env)
- HTTPS/WSS en producción
- SQL injection prevention (ORMs)

---

## Escalabilidad

### Horizontal Scaling
- Stateless API servers (FastAPI)
- Redis para shared state
- RabbitMQ para desacoplamiento
- PostgreSQL read replicas

### Performance
- WebSocket connection pooling
- Redis caching (TTL configurable)
- Vector index optimization (HNSW)
- Batch processing de eventos

### Monitoring
- Health check endpoints
- Prometheus metrics
- Structured logging (JSON)
- APM (futuro: Datadog/New Relic)

---

## Próximos Pasos de Implementación

1. **Setup inicial**
   - Docker Compose con todos los servicios
   - Configuración de entorno (.env)

2. **Backend Core**
   - FastAPI + WebSocket server
   - Authentication middleware
   - PostgreSQL models (SQLAlchemy)

3. **LangGraph Agents**
   - Implementar los 9 nodos
   - Definir tools por nodo
   - State machine transitions

4. **Event Sourcing**
   - RabbitMQ publishers/consumers
   - Event processors
   - Parquet serialization

5. **Frontend Extension**
   - WebSocket client
   - TreeView con estados en tiempo real
   - Webviews reactivos

6. **Integration & Testing**
   - End-to-end tests
   - Load testing
   - Security audit
