# Chat en Tiempo Real - FastAPI + React + Docker

Sistema de chat completo usando FastAPI (backend), React (frontend) y WebSockets, todo dockerizado.

## Características

### Backend (FastAPI)
- ✅ WebSockets nativos de FastAPI
- ✅ API REST para estadísticas
- ✅ Salas de chat múltiples
- ✅ Historial de mensajes
- ✅ Gestión de conexiones
- ✅ Health checks

### Frontend (React)
- ✅ Interfaz moderna con hooks
- ✅ Reconexión automática
- ✅ Indicador de "escribiendo..."
- ✅ Lista de usuarios en tiempo real
- ✅ Mensajes propios resaltados
- ✅ Responsive design

### DevOps
- ✅ Docker Compose
- ✅ Hot reload en desarrollo
- ✅ Variables de entorno
- ✅ Networking entre contenedores

---

## Estructura del Proyecto

```
fastapi-react-chat/
├── backend/
│   ├── main.py              # Servidor FastAPI con WebSockets
│   ├── requirements.txt     # Dependencias Python
│   ├── Dockerfile
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── components/      # Componentes React
│   │   │   ├── LoginScreen.jsx
│   │   │   ├── ChatScreen.jsx
│   │   │   ├── MessageList.jsx
│   │   │   ├── UsersList.jsx
│   │   │   └── MessageInput.jsx
│   │   ├── services/
│   │   │   └── websocketService.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   ├── Dockerfile
│   └── .env.example
│
├── docker-compose.yml       # Orquestación
├── .dockerignore
└── README.md                # Este archivo
```

---

## 🚀 Inicio Rápido con Docker

### Opción 1: Docker Compose (Recomendado)

```bash
# 1. Navegar al proyecto
cd examples/fastapi-react-chat

# 2. Iniciar todo con un comando
docker-compose up

# Backend estará en: http://localhost:8000
# Frontend estará en: http://localhost:3000
```

**¡Listo!** Abre http://localhost:3000 en tu navegador.

### Opción 2: Sin Docker (Desarrollo Local)

**Backend:**

```bash
cd backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
uvicorn main:app --reload --port 8000
```

**Frontend:**

```bash
cd frontend

# Instalar dependencias
npm install

# Ejecutar
npm run dev
```

---

## 📖 Uso

### 1. Abrir la Aplicación

Abre http://localhost:3000 en tu navegador.

### 2. Unirse al Chat

- Ingresa tu nombre de usuario
- Ingresa el nombre de una sala (ej: "general")
- Click en "Unirse al Chat"

### 3. Probar con Múltiples Usuarios

Abre múltiples pestañas/ventanas con diferentes nombres de usuario en la misma sala.

### 4. Características a Probar

- ✅ Enviar mensajes
- ✅ Ver mensajes de otros usuarios
- ✅ Indicador de "escribiendo..."
- ✅ Lista de usuarios en línea
- ✅ Notificaciones de entrada/salida
- ✅ Historial de mensajes al unirse

---

## 🛠️ API Endpoints

### REST API

```bash
# Health check
GET http://localhost:8000/health

# Estadísticas
GET http://localhost:8000/stats

# Salas activas
GET http://localhost:8000/rooms

# Historial de sala
GET http://localhost:8000/rooms/{room_name}/history?limit=50
```

### WebSocket

```
ws://localhost:8000/ws/{username}/{room}
```

**Ejemplo:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/Juan/general');
```

---

## 🐳 Comandos Docker

### Desarrollo

```bash
# Iniciar servicios
docker-compose up

# Iniciar en background
docker-compose up -d

# Ver logs
docker-compose logs -f

# Ver logs de un servicio
docker-compose logs -f backend
docker-compose logs -f frontend

# Detener servicios
docker-compose down

# Reconstruir imágenes
docker-compose build

# Reconstruir y reiniciar
docker-compose up --build
```

### Inspección

```bash
# Ver contenedores
docker-compose ps

# Ejecutar comando en contenedor
docker-compose exec backend bash
docker-compose exec frontend sh

# Ver redes
docker network ls

# Inspeccionar red
docker network inspect fastapi-react-chat_chat-network
```

### Limpieza

```bash
# Detener y eliminar contenedores
docker-compose down

# Eliminar también volúmenes
docker-compose down -v

# Eliminar todo (contenedores, redes, volúmenes)
docker-compose down -v --remove-orphans
```

---

## 🔧 Configuración

### Variables de Entorno

**Backend (.env):**

```env
ENVIRONMENT=development
DEBUG=True
CORS_ORIGINS=http://localhost:3000
```

**Frontend (.env):**

```env
VITE_WS_URL=ws://localhost:8000
VITE_API_URL=http://localhost:8000
```

### Puertos

- Backend: `8000`
- Frontend: `3000`

Para cambiar puertos, edita `docker-compose.yml`:

```yaml
ports:
  - "8001:8000"  # Backend en puerto 8001
  - "3001:3000"  # Frontend en puerto 3001
```

---

## 📡 Flujo de Comunicación WebSocket

```
1. Usuario ingresa nombre y sala
   └─> Frontend conecta: ws://backend:8000/ws/Juan/general

2. Backend acepta conexión
   └─> Envía historial de mensajes
   └─> Notifica a otros usuarios

3. Usuario envía mensaje
   └─> Frontend: websocket.send(JSON.stringify({type:'message', text:'Hola'}))
   └─> Backend: recibe y broadcast a toda la sala

4. Otros usuarios reciben mensaje
   └─> Frontend: websocket.onmessage → actualiza UI

5. Usuario desconecta
   └─> Backend: limpia conexión
   └─> Notifica a otros usuarios
```

---

## 🎨 Componentes React

### LoginScreen
- Formulario de entrada
- Validación
- Animaciones

### ChatScreen
- Contenedor principal
- Gestión de estado
- WebSocket connection

### MessageList
- Renderiza mensajes
- Scroll automático
- Mensajes del sistema

### UsersList
- Sidebar de usuarios
- Estado en línea
- Usuario actual resaltado

### MessageInput
- Input de texto
- Indicador de escritura
- Envío de mensajes

---

## 🔍 Debugging

### Ver logs en tiempo real

```bash
# Todos los logs
docker-compose logs -f

# Solo backend
docker-compose logs -f backend | grep "INFO"

# Solo frontend
docker-compose logs -f frontend
```

### Inspeccionar WebSocket en el navegador

1. Abre DevTools (F12)
2. Ve a Network → WS
3. Selecciona la conexión WebSocket
4. Ve a Messages para ver el tráfico

### Probar API con curl

```bash
# Health check
curl http://localhost:8000/health

# Estadísticas
curl http://localhost:8000/stats

# Salas activas
curl http://localhost:8000/rooms
```

---

## 🚨 Troubleshooting

### Backend no se conecta

```bash
# Verificar que el contenedor esté corriendo
docker-compose ps

# Ver logs del backend
docker-compose logs backend

# Reiniciar backend
docker-compose restart backend
```

### Frontend no carga

```bash
# Limpiar caché de node_modules
docker-compose down
docker-compose up --build

# O manualmente:
cd frontend
rm -rf node_modules
npm install
```

### WebSocket no conecta

1. Verifica que backend esté corriendo: http://localhost:8000/health
2. Verifica la URL del WebSocket en `.env` del frontend
3. Revisa la consola del navegador (F12)
4. Verifica CORS en el backend

### Puerto ocupado

```bash
# Cambiar puerto en docker-compose.yml
ports:
  - "8001:8000"  # Usar 8001 en lugar de 8000
```

---

## 📊 Arquitectura Técnica

### Backend (FastAPI)

```python
# WebSocket endpoint
@app.websocket("/ws/{username}/{room}")
async def websocket_endpoint(websocket, username, room):
    await manager.connect(websocket, username, room)
    # Loop de mensajes
    while True:
        data = await websocket.receive_text()
        # Procesar y broadcast
```

### Frontend (React)

```javascript
// Servicio WebSocket
class WebSocketService {
  connect(username, room) {
    this.ws = new WebSocket(`ws://.../${username}/${room}`);
    this.ws.onmessage = (event) => {
      // Emitir eventos a componentes
    }
  }
}
```

### Docker Networking

```
┌─────────────┐      ┌─────────────┐
│  Frontend   │─────▶│   Backend   │
│  (React)    │      │  (FastAPI)  │
│  Port 3000  │◀─────│  Port 8000  │
└─────────────┘      └─────────────┘
       │                     │
       └─────────────────────┘
           chat-network
```

---

## 🎯 Próximos Pasos

### Para Aprender

1. Lee el código de `backend/main.py` - WebSocket server
2. Revisa `frontend/src/services/websocketService.js` - Client
3. Experimenta modificando componentes React
4. Agrega nuevas características (ver abajo)

### Mejoras Sugeridas

- [ ] Persistencia con base de datos (PostgreSQL)
- [ ] Autenticación con JWT
- [ ] Envío de archivos/imágenes
- [ ] Emojis y reacciones
- [ ] Mensajes privados entre usuarios
- [ ] Notificaciones de navegador
- [ ] Temas claro/oscuro
- [ ] Markdown en mensajes

---

## 📚 Recursos

- [FastAPI WebSockets](https://fastapi.tiangolo.com/advanced/websockets/)
- [React Hooks](https://react.dev/reference/react)
- [Docker Compose](https://docs.docker.com/compose/)
- [WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)

---

## 📝 Licencia

MIT License - Uso libre para aprendizaje y proyectos personales.

---

**¡Feliz codificación!** 🚀

Si tienes preguntas o encuentras problemas, revisa la sección de Troubleshooting o los logs de Docker.
