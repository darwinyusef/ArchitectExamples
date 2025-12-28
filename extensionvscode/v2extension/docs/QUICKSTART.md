# Quick Start - AI Goals Tracker V2

## 🚀 Inicio Rápido (5 minutos)

### Requisitos
- Docker Desktop instalado y corriendo
- Node.js 18+ instalado
- OpenAI API Key

### Paso 1: Configurar Variables de Entorno (1 min)

```bash
cd v2extension/backend
cp .env.example .env
```

Editar `.env` y agregar:
```bash
OPENAI_API_KEY=sk-tu-api-key-aqui
SECRET_KEY=un-string-secreto-de-minimo-32-caracteres-aqui
```

### Paso 2: Iniciar Servicios (2 min)

```bash
# Desde v2extension/
docker-compose up -d
```

Esperar a que todos los servicios estén saludables:
```bash
docker-compose ps
```

Deberías ver:
- ✅ ai_goals_postgres (healthy)
- ✅ ai_goals_redis (healthy)
- ✅ ai_goals_rabbitmq (healthy)
- ✅ ai_goals_minio (healthy)
- ✅ ai_goals_backend (running)

### Paso 3: Verificar Backend (30 seg)

```bash
# Health check
curl http://localhost:8000/health

# Respuesta esperada:
# {"status":"healthy","service":"AI Goals Tracker API","version":"2.0.0"}
```

Ver documentación interactiva:
```
http://localhost:8000/docs
```

### Paso 4: Instalar y Ejecutar Frontend (1.5 min)

```bash
cd frontend
npm install
npm run compile
code .
```

En VS Code:
1. Presionar `F5` para ejecutar la extensión
2. Se abrirá una nueva ventana de VS Code
3. Buscar "AI Goals Tracker" en la barra lateral
4. La extensión se conectará automáticamente al backend

## 🎯 Probar la Conexión

### Desde VS Code

1. Abrir Command Palette (`Cmd+Shift+P` o `Ctrl+Shift+P`)
2. Buscar "AI Goals Tracker: Connect to Server"
3. Ver en la barra de estado: ✅ AI Goals (verde = conectado)

### Desde la Línea de Comandos

```bash
# Probar WebSocket (necesitas websocat)
brew install websocat  # macOS
# o
apt-get install websocat  # Linux

# Conectar
websocat "ws://localhost:8000/api/v1/ws?token=placeholder-token"

# Enviar ping
{"type": "ping", "payload": {"timestamp": 1234567890}, "correlation_id": "test-1"}

# Deberías recibir pong
```

## 📊 Interfaces Web Disponibles

### Backend API Docs
```
http://localhost:8000/docs
Usuario: N/A (público)
```

### RabbitMQ Management
```
http://localhost:15672
Usuario: guest
Password: guest
```

### MinIO Console
```
http://localhost:9001
Usuario: minioadmin
Password: minioadmin
```

## 🐛 Troubleshooting Rápido

### Backend no inicia
```bash
# Ver logs
docker-compose logs backend

# Reiniciar
docker-compose restart backend
```

### Puerto 8000 ya está en uso
```bash
# Cambiar puerto en docker-compose.yml
ports:
  - "8001:8000"  # Cambiar a 8001 o cualquier otro
```

### WebSocket connection refused
```bash
# Verificar que backend esté corriendo
curl http://localhost:8000/health

# Si no responde, reiniciar
docker-compose restart backend
```

### PostgreSQL no está healthy
```bash
# Ver logs
docker-compose logs postgres

# Recrear contenedor
docker-compose down postgres
docker-compose up -d postgres
```

## 📝 Siguiente: Crear tu Primer Goal

### Desde VS Code Extension

1. Click en el icono "+" en la vista "Goals & Tasks"
2. Ingresar título: "Learn Python Basics"
3. El goal se creará y enviará al backend
4. Verás el nuevo goal en la lista

### Desde API (curl)

```bash
curl -X POST http://localhost:8000/api/v1/goals \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Learn Python Basics",
    "description": "Master Python fundamentals"
  }'
```

### Desde Python (script)

```python
import asyncio
import websockets
import json

async def create_goal():
    uri = "ws://localhost:8000/api/v1/ws?token=placeholder-token"

    async with websockets.connect(uri) as websocket:
        # Enviar mensaje de creación de goal
        message = {
            "type": "goal.create",
            "payload": {
                "title": "Learn Python Basics",
                "description": "Master fundamentals"
            },
            "correlation_id": "test-123"
        }

        await websocket.send(json.dumps(message))

        # Recibir respuesta
        response = await websocket.recv()
        print(f"Received: {response}")

asyncio.run(create_goal())
```

## 🔄 Reiniciar Todo (Reset)

```bash
# Detener y eliminar todo (incluyendo datos)
docker-compose down -v

# Volver a iniciar
docker-compose up -d

# Nota: Esto eliminará todos los datos en la base de datos
```

## 📚 Siguientes Pasos

1. Leer `README.md` para documentación completa
2. Leer `GETTING_STARTED.md` para guía de desarrollo
3. Explorar `ARQUITECTURA-TECNICA.md` para entender la arquitectura
4. Ver `PROJECT_SUMMARY.md` para estado del proyecto

## 🛠 Comandos Útiles para Desarrollo

```bash
# Ver todos los logs
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f backend

# Reiniciar un servicio
docker-compose restart backend

# Ejecutar comando en contenedor
docker-compose exec backend python -c "print('Hello')"

# Conectar a PostgreSQL
docker-compose exec postgres psql -U postgres -d ai_goals_tracker

# Conectar a Redis
docker-compose exec redis redis-cli

# Ver estadísticas de contenedores
docker stats
```

## 🎓 Recursos de Aprendizaje

- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [LangGraph Quickstart](https://langchain-ai.github.io/langgraph/tutorials/introduction/)
- [VS Code Extension API](https://code.visualstudio.com/api/get-started/your-first-extension)
- [WebSockets en JavaScript](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)

---

**¿Necesitas ayuda?**
- Revisa `GETTING_STARTED.md` para ejemplos de código
- Revisa `README.md` para troubleshooting detallado
- Consulta la documentación de la API en `http://localhost:8000/docs`

¡Feliz desarrollo! 🚀
