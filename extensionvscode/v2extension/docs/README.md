# AI Goals Tracker V2 🎯

Sistema completo de seguimiento de objetivos de código con IA en tiempo real, arquitectura event sourcing, 9 agentes especializados de LangGraph, y rate limiting inteligente con tracking de tokens OpenAI.

## Arquitectura General

```
┌─────────────────────┐          WebSocket          ┌──────────────────────┐
│  VS Code Extension  │◄─────────────────────────────│  FastAPI Backend     │
│  (TypeScript)       │                              │  (Python)            │
│                     │                              │                      │
│  - TreeView         │          HTTP/REST           │  - LangGraph Agents  │
│  - WebSocket Client │◄─────────────────────────────│  - WebSocket Server  │
│  - Webviews         │                              │  - Event Sourcing    │
└─────────────────────┘                              └──────────────────────┘
                                                               │
                                                               │
                    ┌──────────────────────────────────────────┤
                    │                    │                     │
          ┌─────────▼────────┐  ┌────────▼─────────┐  ┌───────▼────────┐
          │  PostgreSQL      │  │    RabbitMQ      │  │     Redis      │
          │  + pgvector      │  │    (Events)      │  │   (State)      │
          └──────────────────┘  └──────────────────┘  └────────────────┘
                                          │
                                   ┌──────▼──────┐
                                   │    MinIO    │
                                   │ (Data Lake) │
                                   └─────────────┘
```

## Stack Tecnológico

### Backend
- **Framework**: FastAPI + Uvicorn (ASGI)
- **Orquestación IA**: LangGraph + LangChain
- **LLM**: OpenAI GPT-4
- **WebSockets**: FastAPI WebSocket + asyncio
- **Message Broker**: RabbitMQ
- **Base de Datos**: PostgreSQL 15+ con pgvector
- **Cache/State**: Redis 7+
- **Storage**: MinIO (S3-compatible)
- **Autenticación**: JWT

### Frontend
- **Runtime**: Node.js 18+
- **Lenguaje**: TypeScript 5+
- **Framework**: VS Code Extension API
- **WebSocket Client**: ws library

## Requisitos Previos

- **Docker** y **Docker Compose**
- **Node.js 18+** (para desarrollo del frontend)
- **Python 3.11+** (para desarrollo del backend)
- **Poetry** (gestor de dependencias Python)
- **OpenAI API Key**

## 🚀 Instalación y Setup

### Paso 1: Clonar Repositorio

```bash
git clone <repo-url>
cd v2extension
```

### Paso 2: Configurar PostgreSQL con pgvector

#### Opción A: Docker (Recomendado)

El `docker-compose.yml` ya incluye PostgreSQL con pgvector:

```bash
# Iniciar solo PostgreSQL
docker-compose up -d postgres

# Verificar que está corriendo
docker-compose ps postgres

# Verificar extensión pgvector
docker-compose exec postgres psql -U postgres -d ai_goals_tracker -c "CREATE EXTENSION IF NOT EXISTS vector;"
docker-compose exec postgres psql -U postgres -d ai_goals_tracker -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
```

#### Opción B: Instalación Manual de pgvector

Si quieres instalar PostgreSQL manualmente con pgvector:

**En Ubuntu/Debian:**

```bash
# 1. Instalar PostgreSQL 15+
sudo apt update
sudo apt install -y postgresql-15 postgresql-server-dev-15

# 2. Instalar dependencias
sudo apt install -y build-essential git

# 3. Clonar y compilar pgvector
cd /tmp
git clone --branch v0.5.1 https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install

# 4. Crear base de datos y extensión
sudo -u postgres psql << EOF
CREATE DATABASE ai_goals_tracker;
\c ai_goals_tracker
CREATE EXTENSION vector;
SELECT * FROM pg_extension WHERE extname = 'vector';
EOF
```

**En macOS:**

```bash
# 1. Instalar PostgreSQL con Homebrew
brew install postgresql@15

# 2. Iniciar PostgreSQL
brew services start postgresql@15

# 3. Instalar pgvector
cd /tmp
git clone --branch v0.5.1 https://github.com/pgvector/pgvector.git
cd pgvector
make
make install

# 4. Crear base de datos
psql postgres << EOF
CREATE DATABASE ai_goals_tracker;
\c ai_goals_tracker
CREATE EXTENSION vector;
SELECT * FROM pg_extension WHERE extname = 'vector';
EOF
```

**En Windows:**

```powershell
# 1. Instalar PostgreSQL desde https://www.postgresql.org/download/windows/

# 2. Descargar pgvector precompilado desde:
# https://github.com/pgvector/pgvector/releases

# 3. Copiar archivos DLL a:
# C:\Program Files\PostgreSQL\15\lib\
# C:\Program Files\PostgreSQL\15\share\extension\

# 4. Crear base de datos
psql -U postgres
CREATE DATABASE ai_goals_tracker;
\c ai_goals_tracker
CREATE EXTENSION vector;
```

#### Verificar Instalación de pgvector

```bash
# Conectar a la base de datos
psql postgresql://postgres:postgres@localhost:5432/ai_goals_tracker

# En el prompt de psql:
SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';

# Resultado esperado:
#  extname | extversion
# ---------+------------
#  vector  | 0.5.1

# Probar creación de vector
CREATE TABLE test_vectors (
    id serial PRIMARY KEY,
    embedding vector(1536)
);

# Insertar vector de prueba
INSERT INTO test_vectors (embedding) VALUES ('[1,2,3]'::vector(3));

# Limpiar
DROP TABLE test_vectors;

# Salir
\q
```

### Paso 3: Configurar Variables de Entorno

```bash
# Crear archivo .env
cat > .env << 'EOF'
# OpenAI (REQUERIDO)
OPENAI_API_KEY=sk-your-key-here

# Security
SECRET_KEY=$(openssl rand -hex 32)

# Redis (usar remoto o local)
REDIS_URL=redis://64.23.150.221:6379/0

# Database (si usas PostgreSQL local)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/ai_goals_tracker
EOF

# Editar y agregar tu OpenAI API Key
nano .env  # o vim .env
```

### Paso 4: Iniciar Servicios

#### Opción A: Docker Compose (Todo en Docker)

```bash
# Levantar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f backend

# Verificar servicios
docker-compose ps
```

Esto iniciará:
- ✅ PostgreSQL + pgvector (puerto 5432)
- ✅ Redis (remoto: 64.23.150.221:6379)
- ✅ RabbitMQ (puerto 5672, UI: 15672)
- ✅ MinIO (puerto 9000, UI: 9001)
- ✅ Backend API (puerto 8000)

#### Opción B: Desarrollo Local (Solo infraestructura en Docker)

```bash
# 1. Levantar solo infraestructura
docker-compose up -d postgres rabbitmq minio

# 2. Configurar backend local
cd backend
cp .env.example .env
# Editar .env con tus valores

# 3. Instalar Poetry
curl -sSL https://install.python-poetry.org | python3 -

# 4. Instalar dependencias
poetry install

# 5. Ejecutar migraciones
poetry run alembic upgrade head

# 6. Iniciar servidor
poetry run python -m app.main

# O usar el script de inicio rápido
chmod +x scripts/quick_start.sh
./scripts/quick_start.sh
```

### Paso 5: Verificar Servicios

#### ✅ Backend API

```bash
# Health check
curl http://localhost:8000/health

# Respuesta esperada:
# {"status":"healthy","version":"2.0.0"}

# API Docs (Swagger)
open http://localhost:8000/docs

# Ver configuración de rate limits
curl http://localhost:8000/api/v1/admin/rate-limits/config
```

#### ✅ PostgreSQL + pgvector

```bash
# Verificar conexión
psql postgresql://postgres:postgres@localhost:5432/ai_goals_tracker

# Verificar extensión vector
psql postgresql://postgres:postgres@localhost:5432/ai_goals_tracker \
  -c "SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';"

# Verificar tablas creadas por migraciones
psql postgresql://postgres:postgres@localhost:5432/ai_goals_tracker \
  -c "\dt"

# Debería mostrar: users, courses, goals, tasks, code_snapshots, events, embeddings, rate_limit_audits
```

#### ✅ Redis

```bash
# Conectar a Redis (si es local)
redis-cli -h localhost -p 6379 ping

# O si usas el remoto
redis-cli -h 64.23.150.221 -p 6379 ping

# Respuesta esperada: PONG
```

#### ✅ RabbitMQ Management UI

```
http://localhost:15672
Usuario: guest
Password: guest
```

Verifica que veas exchanges y queues creados.

#### ✅ MinIO Console

```
http://localhost:9001
Usuario: minioadmin
Password: minioadmin
```

### Paso 6: Ejecutar Migraciones

Las migraciones se ejecutan automáticamente al iniciar el backend con Docker, pero si las necesitas ejecutar manualmente:

```bash
cd backend

# Ver estado actual
poetry run alembic current

# Ver historial de migraciones
poetry run alembic history

# Ejecutar todas las migraciones
poetry run alembic upgrade head

# Las 8 migraciones incluidas:
# 001 - create_users_table
# 002 - create_courses_table
# 003 - create_goals_table
# 004 - create_tasks_table
# 005 - create_code_snapshots_table
# 006 - create_events_table
# 007 - create_embeddings_table (con pgvector)
# 008 - create_rate_limit_audits_table

# Rollback última migración (si necesitas)
poetry run alembic downgrade -1
```

### Paso 7: Probar los Endpoints

```bash
# Crear un objetivo
curl -X POST http://localhost:8000/api/v1/goals \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Learn FastAPI",
    "description": "Master FastAPI framework",
    "user_id": "test-user",
    "course_id": "course-123",
    "priority": "high"
  }'

# Listar objetivos
curl http://localhost:8000/api/v1/goals?user_id=test-user

# Ver estado de rate limits
curl http://localhost:8000/api/v1/admin/rate-limits/users/test-user/status

# Ver documentación completa de tests
cat backend/TESTS_CURL_API.md
```

## 📚 Documentación Adicional

- **[DOCKER_SETUP.md](DOCKER_SETUP.md)** - Guía completa de Docker y troubleshooting
- **[backend/RATE_LIMITING.md](backend/RATE_LIMITING.md)** - Sistema de rate limiting y tracking de tokens
- **[backend/TESTS_CURL_API.md](backend/TESTS_CURL_API.md)** - Tests de todos los endpoints con curl
- **[backend/SERVICIOS_CRUD.md](backend/SERVICIOS_CRUD.md)** - Documentación de servicios CRUD
- **[backend/RESPUESTAS_ENDPOINTS_REALES.md](backend/RESPUESTAS_ENDPOINTS_REALES.md)** - Ejemplos de respuestas reales

## 🧪 Tests

El proyecto incluye tests unitarios para componentes críticos:

```bash
cd backend

# Ejecutar todos los tests
poetry run pytest

# Con coverage
poetry run pytest --cov=app --cov-report=html

# Ver reporte
open htmlcov/index.html

# Tests incluidos:
# - test_rate_limiter.py - Sistema de rate limiting
# - test_openai_tracker.py - Tracking de tokens OpenAI
# - test_services.py - Servicios CRUD
# - test_api.py - Endpoints de API
```

## 🚀 Características Principales

### 1. Rate Limiting Inteligente

- Token Bucket algorithm con Redis
- Tracking automático de tokens OpenAI
- Auditoría completa de requests
- Detección de actividades sospechosas
- Cálculo de costos en tiempo real

```bash
# Ver configuración de rate limits
curl http://localhost:8000/api/v1/admin/rate-limits/config

# Límites configurados:
# - api_call: 100/min (burst 1.5x = 150)
# - embedding_generation: 20/min (burst 1.2x = 24)
# - chat_completion: 10/min (sin burst)
# - code_validation: 30/min (burst 1.3x = 39)
# - rag_search: 50/min (burst 1.5x = 75)
```

### 2. RAG con pgvector

- Búsqueda semántica de objetivos similares
- Búsqueda de código similar validado
- Scope configurable: usuario, curso, o global

```python
# Buscar objetivos similares
similar_goals = await get_similar_goals(
    query="Learn Python programming",
    user_id="user_123",
    scope="user",  # o "course" o "global"
    limit=5
)

# Buscar código similar
similar_code = await get_similar_code(
    code="async def get_user(db, user_id): ...",
    user_id="user_123",
    language="python",
    scope="course"  # Aprender de otros estudiantes
)
```

### 3. WebSockets en Tiempo Real

```javascript
// Conectar a WebSocket
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/user_123');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Event:', data);
};

// Suscribirse a eventos
ws.send(JSON.stringify({
  type: 'subscribe',
  channels: ['goals', 'tasks', 'code_validation']
}));
```

### 4. LangGraph Agents

9 agentes especializados para gestión inteligente de objetivos y tareas.

Ver documentación completa en `backend/app/agents/`

## 🔧 Configuración Avanzada

### Rate Limits Personalizados

Editar `backend/app/core/rate_limiter.py`:

```python
configs = {
    "embedding_generation": RateLimitConfig(
        max_requests=50,  # Aumentar de 20 a 50
        window_seconds=60,
        burst_multiplier=2.0  # Permitir más bursts
    ),
}
```

### PostgreSQL Tuning para pgvector

Editar `postgresql.conf`:

```conf
# Optimizar para búsquedas de vectores
shared_buffers = 2GB
effective_cache_size = 6GB
maintenance_work_mem = 512MB
max_parallel_workers_per_gather = 4
```

## 📊 Monitoreo

### Métricas de Rate Limiting

```sql
-- Block rate (última hora)
SELECT
    COUNT(*) FILTER (WHERE NOT allowed) * 100.0 / COUNT(*) as block_rate
FROM rate_limit_audits
WHERE timestamp > NOW() - INTERVAL '1 hour';

-- Top usuarios por costo OpenAI
SELECT
    user_id,
    SUM(openai_total_tokens) as tokens,
    SUM(estimated_cost_cents) / 100.0 as cost_usd
FROM rate_limit_audits
WHERE timestamp::date = CURRENT_DATE
GROUP BY user_id
ORDER BY cost_usd DESC
LIMIT 10;
```

## 🐛 Troubleshooting

### PostgreSQL no inicia

```bash
# Ver logs
docker-compose logs postgres

# Verificar permisos de volumen
docker volume inspect v2extension_postgres_data

# Reiniciar
docker-compose restart postgres
```

### Error: "pgvector extension not found"

```bash
# Verificar extensión
docker-compose exec postgres psql -U postgres -d ai_goals_tracker \
  -c "CREATE EXTENSION IF NOT EXISTS vector;"

# Si falla, verificar imagen Docker
docker-compose exec postgres psql -U postgres \
  -c "SELECT * FROM pg_available_extensions WHERE name = 'vector';"
```

### Backend no inicia

```bash
# Ver logs detallados
docker-compose logs backend

# Verificar variables de entorno
docker-compose exec backend env | grep -E "DATABASE|OPENAI|REDIS"

# Ejecutar validación de imports (requiere Python 3.11+)
docker-compose exec backend python scripts/validate_imports.py
```

Para más troubleshooting, ver [DOCKER_SETUP.md](DOCKER_SETUP.md).

## 📝 Licencia

[Especificar licencia]

## 👥 Autores

- Tu Nombre

---

**Versión:** 2.0.0
**Última actualización:** Diciembre 2024

**Stack:** FastAPI + LangGraph + PostgreSQL (pgvector) + Redis + RabbitMQ
npm install
npm run compile
```

#### Ejecutar en Modo Desarrollo

1. Abrir `frontend/` en VS Code
2. Presionar `F5` para abrir una nueva ventana de VS Code con la extensión cargada
3. La extensión se conectará automáticamente al backend en `ws://localhost:8000/api/v1/ws`

## Estructura del Proyecto

```
v2extension/
├── backend/
│   ├── app/
│   │   ├── agents/           # 9 agentes de LangGraph
│   │   │   ├── graph.py      # Definición del grafo
│   │   │   └── nodes.py      # Implementación de nodos
│   │   ├── api/              # Endpoints REST y WebSocket
│   │   │   ├── auth.py
│   │   │   ├── health.py
│   │   │   └── websocket.py
│   │   ├── core/             # Configuración y servicios base
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   ├── redis_client.py
│   │   │   ├── rabbitmq.py
│   │   │   ├── security.py
│   │   │   └── websocket.py
│   │   ├── models/           # Modelos SQLAlchemy
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── services/         # Lógica de negocio
│   │   │   └── message_router.py
│   │   └── main.py           # Entry point
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── commands/         # Comandos de VS Code
│   │   ├── providers/        # TreeView y Webview providers
│   │   │   ├── goalsTreeProvider.ts
│   │   │   └── connectionStatusProvider.ts
│   │   ├── services/         # Servicios
│   │   │   └── websocket.ts  # Cliente WebSocket
│   │   └── extension.ts      # Entry point
│   ├── package.json
│   └── tsconfig.json
│
├── docker-compose.yml
└── README.md
```

## Los 9 Agentes de LangGraph

### Nodo 1: Authentication & Authorization
- Validar JWT tokens
- Verificar enrollments en cursos
- **Tools**: `validate_token`, `check_enrollment`

### Nodo 2: Goal Generator
- Crear retos de código personalizados
- Generar tareas secuenciales
- **Tools**: `create_goal`, `generate_tasks`, `ai_gen`

### Nodo 3: Course Manager
- Documentar retos en cursos
- Estructurar contenido educativo
- **Tools**: `create_course`, `add_lesson`, `vector_db`

### Nodo 4: Feedback Agent (Continuous)
- Feedback en tiempo real durante coding
- Sugerencias y hints
- **Tools**: `analyze_code`, `give_hint`, `validate`

### Nodo 5: Performance Evaluator
- Evaluar desempeño del usuario
- Enviar eventos al data lake
- **Tools**: `evaluate_perf`, `emit_event`, `to_parquet`

### Nodo 6: State Monitor
- Revisar estados fundamentales del proceso
- Cambiar flujos según necesidad
- **Tools**: `check_state`, `update_flow`, `redis_ops`

### Nodo 7: Context Organizer
- Entender necesidad global del usuario
- Priorizar tareas según contexto
- **Tools**: `analyze_context`, `prioritize`, `search`

### Nodo 8: Emotional Support
- Detectar estado emocional
- Motivar constantemente
- **Tools**: `detect_mood`, `motivate`, `send_modal`

### Nodo 9: Contract Validator
- Verificar condiciones de contrato
- Detectar cambios en términos
- **Tools**: `check_contract`, `validate_terms`

## Flujo de Comunicación WebSocket

### Cliente → Servidor (Mensajes)

```typescript
// Crear goal
{
  "type": "goal.create",
  "payload": {
    "title": "Learn React Hooks",
    "description": "..."
  }
}

// Validar tarea
{
  "type": "task.validate",
  "payload": {
    "task_id": "uuid",
    "code": "function MyComponent() { ... }"
  }
}
```

### Servidor → Cliente (Eventos)

```typescript
// Goal creado
{
  "type": "goal.created",
  "payload": {
    "goal_id": "uuid",
    "title": "Learn React Hooks"
  }
}

// Validación completada
{
  "type": "task.validation_result",
  "payload": {
    "task_id": "uuid",
    "passed": true,
    "feedback": "Great job!"
  }
}

// Motivación (Nodo 8)
{
  "type": "motivation.sent",
  "payload": {
    "message": "You're doing amazing! Keep it up!"
  }
}
```

## Desarrollo

### Backend

#### Instalar dependencias
```bash
cd backend
poetry install
```

#### Ejecutar sin Docker
```bash
poetry run uvicorn app.main:app --reload
```

#### Tests
```bash
poetry run pytest
```

#### Linting
```bash
poetry run ruff check .
poetry run black .
```

### Frontend

#### Instalar dependencias
```bash
cd frontend
npm install
```

#### Compilar
```bash
npm run compile
```

#### Watch mode
```bash
npm run watch
```

#### Ejecutar extensión
Presionar `F5` en VS Code

## Configuración de la Extensión

Abrir Settings en VS Code y buscar "AI Goals V2":

```json
{
  "aiGoalsV2.serverUrl": "ws://localhost:8000/api/v1/ws",
  "aiGoalsV2.apiUrl": "http://localhost:8000/api/v1",
  "aiGoalsV2.autoConnect": true,
  "aiGoalsV2.reconnectInterval": 5000
}
```

## Event Sourcing

Todos los eventos se publican a RabbitMQ con routing keys:

```
user.registered
user.logged_in
goal.created
goal.started
task.validated
feedback.generated
performance.evaluated
mood.detected
```

Los eventos se procesan y almacenan en:
- **PostgreSQL**: Estado actual
- **MinIO**: Eventos en formato Parquet (data lake)

## Próximos Pasos

1. **Implementar autenticación real**
   - Login/Register en frontend
   - Integración con backend JWT

2. **Completar modelos de base de datos**
   - SQLAlchemy models
   - Alembic migrations

3. **Implementar tools de LangGraph**
   - Cada nodo necesita sus tools específicas
   - Integración con OpenAI function calling

4. **Event processors**
   - Consumidores de RabbitMQ
   - Escritura a MinIO (Parquet)

5. **Tests**
   - Unit tests (backend y frontend)
   - Integration tests
   - E2E tests

## Troubleshooting

### Backend no se conecta a PostgreSQL
```bash
docker-compose logs postgres
docker-compose restart postgres
```

### WebSocket connection refused
Verificar que el backend esté corriendo:
```bash
curl http://localhost:8000/health
```

### RabbitMQ no está disponible
```bash
docker-compose logs rabbitmq
docker-compose restart rabbitmq
```

## Licencia

MIT

## Contacto

Para preguntas o sugerencias, crear un issue en el repositorio.
