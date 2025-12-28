# Getting Started - AI Goals Tracker V2

Guía rápida para comenzar a desarrollar con AI Goals Tracker V2.

## Quick Start (5 minutos)

### 1. Clonar y Configurar

```bash
# Clonar repositorio
git clone <repo-url>
cd v2extension

# Configurar backend
cd backend
cp .env.example .env
# Editar .env y agregar OPENAI_API_KEY
```

### 2. Iniciar Todo con Docker

```bash
# Desde v2extension/
docker-compose up -d

# Esperar a que todos los servicios estén healthy
docker-compose ps
```

### 3. Probar Backend

```bash
# Health check
curl http://localhost:8000/health

# API docs
open http://localhost:8000/docs
```

### 4. Instalar y Ejecutar Frontend

```bash
cd frontend
npm install
npm run compile

# Abrir en VS Code
code .

# Presionar F5 para ejecutar la extensión
```

## Desarrollo del Backend

### Estructura de Archivos

```
backend/app/
├── main.py              # Entry point, FastAPI app
├── core/                # Configuración base
│   ├── config.py        # Settings (Pydantic)
│   ├── database.py      # SQLAlchemy setup
│   ├── redis_client.py  # Redis operations
│   ├── rabbitmq.py      # RabbitMQ pub/sub
│   ├── security.py      # JWT, passwords
│   └── websocket.py     # WebSocket manager
├── api/                 # Endpoints
│   ├── auth.py          # /auth/login, /auth/register
│   ├── health.py        # /health
│   └── websocket.py     # /ws
├── agents/              # LangGraph agents
│   ├── graph.py         # Workflow definition
│   └── nodes.py         # Agent implementations
├── models/              # SQLAlchemy ORM
├── schemas/             # Pydantic schemas
└── services/            # Business logic
```

### Agregar un Nuevo Endpoint

1. Crear schema en `app/schemas/`:

```python
# app/schemas/goal.py
from pydantic import BaseModel

class CreateGoalRequest(BaseModel):
    title: str
    description: str

class GoalResponse(BaseModel):
    id: str
    title: str
    status: str
```

2. Crear endpoint en `app/api/`:

```python
# app/api/goals.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.goal import CreateGoalRequest, GoalResponse

router = APIRouter()

@router.post("/goals", response_model=GoalResponse)
async def create_goal(
    request: CreateGoalRequest,
    db: AsyncSession = Depends(get_db)
):
    # Implementar lógica
    return GoalResponse(id="uuid", title=request.title, status="pending")
```

3. Registrar en `app/api/__init__.py`:

```python
from app.api import goals

router.include_router(goals.router, prefix="/goals", tags=["Goals"])
```

### Agregar un Tool a un Agente

1. Crear tool en `app/tools/`:

```python
# app/tools/code_analyzer.py
from langchain.tools import tool

@tool
async def analyze_code(code: str) -> dict:
    """Analyze code quality and style."""
    # Implementar análisis con OpenAI
    return {"score": 85, "suggestions": [...]}
```

2. Usar en nodo:

```python
# app/agents/nodes.py
from app.tools.code_analyzer import analyze_code

async def feedback_node(state: AgentState) -> dict:
    code = state.get("code_snapshot", "")
    result = await analyze_code.ainvoke(code)

    return {
        "validation_results": result,
        "current_node": "nodo_4_feedback"
    }
```

### Emitir Eventos a RabbitMQ

```python
from app.core.rabbitmq import EventPublisher, EventTypes

publisher = EventPublisher()

await publisher.publish(
    routing_key=EventTypes.GOAL_CREATED,
    payload={
        "goal_id": "uuid",
        "user_id": "uuid",
        "timestamp": "2025-12-28T00:00:00Z"
    }
)
```

## Desarrollo del Frontend

### Estructura de Archivos

```
frontend/src/
├── extension.ts         # Entry point
├── commands/            # VS Code commands
│   └── index.ts
├── providers/           # UI providers
│   ├── goalsTreeProvider.ts
│   └── connectionStatusProvider.ts
└── services/            # Services
    └── websocket.ts     # WebSocket client
```

### Enviar Mensaje al Backend

```typescript
// En cualquier parte del código
import { wsClient } from './services/websocket';

wsClient.send('goal.create', {
    title: 'My New Goal',
    description: 'Learn TypeScript'
});
```

### Escuchar Eventos del Backend

```typescript
// En extension.ts
wsClient.on('goal.created', (data) => {
    vscode.window.showInformationMessage(`Goal created: ${data.title}`);
    goalsTreeProvider.refresh();
});
```

### Agregar Nuevo Comando

1. Definir en `package.json`:

```json
{
  "contributes": {
    "commands": [
      {
        "command": "aiGoalsV2.myNewCommand",
        "title": "My New Command",
        "icon": "$(star)"
      }
    ]
  }
}
```

2. Implementar en `src/commands/index.ts`:

```typescript
context.subscriptions.push(
    vscode.commands.registerCommand('aiGoalsV2.myNewCommand', async () => {
        const input = await vscode.window.showInputBox({
            prompt: 'Enter something'
        });

        if (input) {
            wsClient.send('my.action', { value: input });
        }
    })
);
```

### Crear Nueva Vista Webview

```typescript
// src/providers/myWebviewProvider.ts
import * as vscode from 'vscode';

export class MyWebviewProvider implements vscode.WebviewViewProvider {
    public resolveWebviewView(webviewView: vscode.WebviewView) {
        webviewView.webview.options = {
            enableScripts: true
        };

        webviewView.webview.html = `
            <!DOCTYPE html>
            <html>
            <body>
                <h1>My Custom View</h1>
                <button onclick="handleClick()">Click me</button>
                <script>
                    const vscode = acquireVsCodeApi();
                    function handleClick() {
                        vscode.postMessage({ type: 'buttonClicked' });
                    }
                </script>
            </body>
            </html>
        `;

        webviewView.webview.onDidReceiveMessage(data => {
            if (data.type === 'buttonClicked') {
                vscode.window.showInformationMessage('Button clicked!');
            }
        });
    }
}
```

## Trabajar con Base de Datos

### Crear un Modelo

```python
# app/models/goal.py
from sqlalchemy import Column, String, Text, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import uuid

class Goal(Base):
    __tablename__ = "goals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id"))
    difficulty = Column(String(50))
```

### Usar en Endpoint

```python
from sqlalchemy import select
from app.models.goal import Goal

@router.get("/goals")
async def get_goals(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Goal))
    goals = result.scalars().all()
    return [{"id": str(g.id), "title": g.title} for g in goals]
```

### Crear Migración (Alembic)

```bash
cd backend

# Inicializar Alembic (solo primera vez)
poetry run alembic init migrations

# Crear migración
poetry run alembic revision --autogenerate -m "Add goals table"

# Aplicar migración
poetry run alembic upgrade head
```

## Debugging

### Backend

1. En VS Code, crear `.vscode/launch.json` en `backend/`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: FastAPI",
            "type": "python",
            "request": "launch",
            "module": "uvicorn",
            "args": [
                "app.main:app",
                "--reload",
                "--host", "0.0.0.0",
                "--port", "8000"
            ],
            "jinja": true,
            "justMyCode": false
        }
    ]
}
```

2. Presionar F5 para iniciar debugger

### Frontend

1. Abrir `frontend/` en VS Code
2. Presionar F5
3. Se abrirá nueva ventana de VS Code con la extensión
4. Puedes poner breakpoints en el código TypeScript

### WebSocket

Usar una herramienta como **Postman** o **websocat**:

```bash
# Instalar websocat
brew install websocat

# Conectar a WebSocket
websocat "ws://localhost:8000/api/v1/ws?token=your-jwt-token"

# Enviar mensaje
{"type": "ping", "payload": {"timestamp": 1234567890}}
```

## Testing

### Backend Tests

```bash
cd backend
poetry run pytest

# Con coverage
poetry run pytest --cov=app --cov-report=html
```

Crear test:

```python
# backend/tests/test_goals.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_goal():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/v1/goals", json={
            "title": "Test Goal",
            "description": "Test"
        })

    assert response.status_code == 201
    assert response.json()["title"] == "Test Goal"
```

### Frontend Tests

```bash
cd frontend
npm test
```

## Recursos Útiles

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [LangChain Docs](https://python.langchain.com/)
- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
- [VS Code Extension API](https://code.visualstudio.com/api)
- [SQLAlchemy 2.0 Docs](https://docs.sqlalchemy.org/)

## Comandos Útiles

```bash
# Ver logs de servicios
docker-compose logs -f backend
docker-compose logs -f postgres
docker-compose logs -f rabbitmq

# Reiniciar servicios
docker-compose restart backend
docker-compose down && docker-compose up -d

# Conectar a PostgreSQL
docker-compose exec postgres psql -U postgres -d ai_goals_tracker

# Conectar a Redis
docker-compose exec redis redis-cli

# Ver mensajes en RabbitMQ
# Ir a http://localhost:15672 (guest/guest)
```

## Próximos Pasos

1. Leer `ARQUITECTURA-TECNICA.md` para entender la arquitectura completa
2. Explorar `backend/app/agents/` para ver los 9 nodos de LangGraph
3. Implementar tu primer tool en `backend/app/tools/`
4. Crear tu primer comando en el frontend

¡Feliz desarrollo! 🚀
