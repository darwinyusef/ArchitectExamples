# Estructura del Proyecto WebSocket Chat

## Árbol de Archivos

```
websockets/
│
├── README.md                    # Documentación principal
├── QUICKSTART.md               # Guía de inicio rápido
├── GUIA_WEBSOCKETS.md          # Guía completa de WebSockets
├── PROYECTO_ESTRUCTURA.md      # Este archivo
├── .gitignore                  # Archivos ignorados por Git
├── docker-compose.yml          # Configuración Docker Compose
│
├── backend/                    # Servidor FastAPI
│   ├── main.py                # Punto de entrada del servidor
│   ├── requirements.txt       # Dependencias Python
│   ├── .env.example          # Ejemplo de variables de entorno
│   └── Dockerfile            # Imagen Docker del backend
│
└── frontend/                   # Cliente React
    ├── public/               # Archivos estáticos
    ├── src/
    │   ├── components/       # Componentes React
    │   │   ├── ChatRoom.jsx        # Sala de chat
    │   │   ├── ChatRoom.css
    │   │   ├── Login.jsx           # Formulario de login
    │   │   └── Login.css
    │   ├── hooks/            # Custom hooks
    │   │   └── useWebSocket.js     # Hook WebSocket
    │   ├── App.jsx          # Componente principal
    │   ├── App.css
    │   ├── main.jsx         # Punto de entrada React
    │   └── index.css        # Estilos globales
    ├── package.json          # Dependencias Node.js
    ├── vite.config.js       # Configuración Vite
    └── Dockerfile           # Imagen Docker del frontend
```

## Descripción de Archivos Principales

### Backend (FastAPI)

#### `backend/main.py`
Servidor principal que maneja:
- Conexiones WebSocket
- Gestión de usuarios conectados
- Broadcast de mensajes
- Eventos de conexión/desconexión
- Endpoints HTTP para health check

**Clases principales:**
- `ConnectionManager`: Gestiona las conexiones activas

**Endpoints:**
- `GET /`: Información del servidor
- `GET /health`: Estado y estadísticas
- `WebSocket /ws/{username}`: Conexión WebSocket

#### `backend/requirements.txt`
Dependencias Python:
- `fastapi`: Framework web
- `uvicorn`: Servidor ASGI
- `websockets`: Soporte WebSocket
- `python-multipart`: Manejo de formularios

### Frontend (React)

#### `frontend/src/App.jsx`
Componente raíz que maneja:
- Estado de autenticación
- Navegación entre Login y ChatRoom
- Gestión de username

#### `frontend/src/components/Login.jsx`
Formulario de ingreso que:
- Solicita nombre de usuario
- Valida entrada
- Redirige al chat

#### `frontend/src/components/ChatRoom.jsx`
Sala de chat principal que:
- Muestra mensajes en tiempo real
- Lista usuarios conectados
- Permite enviar mensajes
- Muestra notificaciones del sistema
- Maneja reconexión

#### `frontend/src/hooks/useWebSocket.js`
Hook personalizado que:
- Establece conexión WebSocket
- Maneja eventos (open, message, error, close)
- Implementa reconexión automática
- Gestiona estado de conexión
- Provee función para enviar mensajes

## Flujo de Datos

```
┌─────────────────────────────────────────────────────────┐
│                    Usuario Ingresa                      │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
         ┌──────────────────────┐
         │   Login Component    │
         │  (Solicita username) │
         └──────────┬───────────┘
                    │
                    │ username válido
                    ▼
         ┌──────────────────────┐
         │  App Component       │
         │  (setIsLoggedIn)     │
         └──────────┬───────────┘
                    │
                    ▼
         ┌──────────────────────────────┐
         │     ChatRoom Component       │
         │  - Muestra UI del chat       │
         │  - Usa useWebSocket hook     │
         └──────────┬───────────────────┘
                    │
                    ▼
         ┌──────────────────────────────┐
         │   useWebSocket Hook          │
         │  - Crea conexión WS          │
         │  - Maneja eventos            │
         │  - Almacena mensajes         │
         └──────────┬───────────────────┘
                    │
                    │ ws://localhost:8000/ws/username
                    ▼
┌────────────────────────────────────────────────────────┐
│              Backend WebSocket Server                  │
│  ┌──────────────────────────────────────────────────┐ │
│  │         ConnectionManager                        │ │
│  │  - accept(): Acepta conexión                     │ │
│  │  - broadcast(): Envía a todos                    │ │
│  │  - disconnect(): Remueve conexión                │ │
│  └──────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────┘
                    │
                    │ Broadcast a todos los clientes
                    ▼
         ┌──────────────────────────────┐
         │  Todos los clientes          │
         │  conectados reciben          │
         │  el mensaje                  │
         └──────────────────────────────┘
```

## Flujo de Mensajes

### 1. Usuario envía mensaje

```javascript
// Frontend: ChatRoom.jsx
const handleSubmit = (e) => {
  e.preventDefault()
  sendMessage(message)  // → useWebSocket hook
}

// Frontend: useWebSocket.js
const sendMessage = (message) => {
  ws.current.send(JSON.stringify({ message }))
}
```

### 2. Servidor recibe y procesa

```python
# Backend: main.py
@app.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    data = await websocket.receive_text()
    message_data = json.loads(data)

    broadcast_message = {
        "type": "message",
        "username": username,
        "message": message_data.get("message"),
        "timestamp": datetime.now().isoformat()
    }

    await manager.broadcast(broadcast_message)
```

### 3. Todos los clientes reciben

```javascript
// Frontend: useWebSocket.js
ws.current.onmessage = (event) => {
  const data = JSON.parse(event.data)
  setMessages(prev => [...prev, data])
}
```

### 4. ChatRoom renderiza

```javascript
// Frontend: ChatRoom.jsx
{messages.map((msg, index) => (
  <div key={index}>
    <span>{msg.username}:</span> {msg.message}
  </div>
))}
```

## Estados de la Aplicación

### Estados del Frontend

```javascript
// App.jsx
const [username, setUsername] = useState('')
const [isLoggedIn, setIsLoggedIn] = useState(false)

// ChatRoom.jsx
const [message, setMessage] = useState('')

// useWebSocket.js
const [messages, setMessages] = useState([])
const [isConnected, setIsConnected] = useState(false)
const [onlineUsers, setOnlineUsers] = useState(0)
```

### Estados del Backend

```python
# ConnectionManager
self.active_connections: List[WebSocket] = []
self.users: Dict[WebSocket, str] = {}
```

## Tipos de Mensajes WebSocket

### 1. Mensaje de Chat
```json
{
  "type": "message",
  "username": "Juan",
  "message": "Hola!",
  "timestamp": "2025-12-09T12:34:56.789Z"
}
```

### 2. Usuario Conectado
```json
{
  "type": "user_joined",
  "username": "María",
  "timestamp": "2025-12-09T12:34:56.789Z",
  "online_users": 3
}
```

### 3. Usuario Desconectado
```json
{
  "type": "user_left",
  "username": "Pedro",
  "timestamp": "2025-12-09T12:34:56.789Z",
  "online_users": 2
}
```

## Características Implementadas

### Backend
- ✅ Gestión de conexiones WebSocket
- ✅ Broadcast de mensajes
- ✅ Tracking de usuarios
- ✅ Manejo de desconexiones
- ✅ CORS configurado
- ✅ Health check endpoint
- ✅ Timestamps en mensajes

### Frontend
- ✅ Autenticación simple
- ✅ Chat en tiempo real
- ✅ Indicador de conexión
- ✅ Contador de usuarios
- ✅ Reconexión automática
- ✅ Scroll automático
- ✅ Validación de inputs
- ✅ Diseño responsivo
- ✅ Notificaciones de sistema
- ✅ Distinción de mensajes propios

## Patrones de Diseño Utilizados

### Backend
- **Singleton**: ConnectionManager (única instancia)
- **Observer**: WebSocket connections (notificación a múltiples clientes)
- **Manager Pattern**: Gestión centralizada de conexiones

### Frontend
- **Custom Hook**: useWebSocket (lógica reutilizable)
- **Component Composition**: Login + ChatRoom
- **Controlled Components**: Formularios controlados
- **State Lifting**: Estado compartido en App

## Tecnologías y Versiones

### Backend
- Python 3.8+
- FastAPI 0.109.0
- Uvicorn 0.27.0
- WebSockets 12.0

### Frontend
- React 19.2.0
- Vite 7.2.4
- Node.js 16+

## Puertos

| Servicio | Puerto | Protocolo |
|----------|--------|-----------|
| Backend HTTP | 8000 | HTTP |
| Backend WS | 8000 | WebSocket |
| Frontend Dev | 5173 | HTTP |

## Variables de Entorno

### Backend (.env)
```env
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Frontend
Configurado en código:
- WebSocket URL: `ws://localhost:8000/ws`

## Próximas Mejoras Sugeridas

### Funcionalidad
1. Salas/Rooms de chat
2. Mensajes privados
3. Persistencia en base de datos
4. Autenticación JWT
5. Carga de archivos
6. Emojis y reacciones
7. Typing indicators
8. Historial de mensajes

### Técnicas
1. Tests unitarios y E2E
2. Redis para escalabilidad
3. Rate limiting
4. Message queue
5. Logging avanzado
6. Metrics y monitoring
7. CI/CD pipeline
8. Production build optimizado

## Recursos de Aprendizaje

1. **GUIA_WEBSOCKETS.md**: Guía completa de WebSockets
2. **README.md**: Documentación del proyecto
3. **QUICKSTART.md**: Inicio rápido

## Comandos Rápidos

### Desarrollo
```bash
# Backend
cd backend && python main.py

# Frontend
cd frontend && npm run dev
```

### Docker
```bash
docker-compose up --build
```

### Testing
```bash
# Health check
curl http://localhost:8000/health

# WebSocket test
wscat -c ws://localhost:8000/ws/TestUser
```

---

Este proyecto es una base sólida para aprender WebSockets y construir aplicaciones en tiempo real. ¡Experimenta y extiéndelo según tus necesidades!
