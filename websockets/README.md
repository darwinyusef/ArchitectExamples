# WebSocket Chat Application

Aplicación de chat en tiempo real construida con **FastAPI** (backend) y **React** (frontend) utilizando WebSockets.

## Características

- Chat en tiempo real con múltiples usuarios
- Notificaciones de usuarios conectados/desconectados
- Contador de usuarios en línea
- Interfaz moderna y responsiva
- Reconexión automática
- Indicador de estado de conexión

## Estructura del Proyecto

```
websockets/
├── backend/
│   ├── main.py              # Servidor FastAPI con WebSockets
│   ├── requirements.txt     # Dependencias de Python
│   └── .env.example        # Variables de entorno
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatRoom.jsx    # Componente de sala de chat
│   │   │   ├── ChatRoom.css
│   │   │   ├── Login.jsx       # Componente de login
│   │   │   └── Login.css
│   │   ├── hooks/
│   │   │   └── useWebSocket.js # Hook personalizado para WebSocket
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── index.css
│   ├── package.json
│   └── vite.config.js
├── GUIA_WEBSOCKETS.md      # Guía completa de WebSockets
└── README.md               # Este archivo
```

## Requisitos Previos

- **Python 3.8+**
- **Node.js 16+** y npm
- Terminal o línea de comandos

## Instalación

### 1. Clonar o Navegar al Proyecto

```bash
cd websockets
```

### 2. Configurar el Backend

```bash
# Navegar a la carpeta backend
cd backend

# Crear entorno virtual (opcional pero recomendado)
python -m venv venv

# Activar entorno virtual
# En macOS/Linux:
source venv/bin/activate
# En Windows:
# venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Configurar el Frontend

```bash
# Navegar a la carpeta frontend (desde la raíz)
cd frontend

# Instalar dependencias
npm install
```

## Ejecución

### Iniciar el Backend

```bash
# Desde la carpeta backend
cd backend

# Asegúrate de tener el entorno virtual activado si lo creaste
# source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate     # Windows

# Iniciar el servidor
python main.py

# O usando uvicorn directamente:
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

El servidor estará disponible en:
- **API**: http://localhost:8000
- **WebSocket**: ws://localhost:8000/ws/{username}
- **Docs**: http://localhost:8000/docs

### Iniciar el Frontend

```bash
# Desde la carpeta frontend (en otra terminal)
cd frontend

# Iniciar el servidor de desarrollo
npm run dev
```

La aplicación estará disponible en: **http://localhost:5173**

## Uso

1. Abre tu navegador en http://localhost:5173
2. Ingresa un nombre de usuario
3. Haz clic en "Join Chat"
4. Comienza a chatear en tiempo real

Para probar con múltiples usuarios, abre varias ventanas del navegador y conecta diferentes usuarios.

## Endpoints de la API

### HTTP Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/` | Información del servidor |
| GET | `/health` | Estado del servidor y conexiones activas |

### WebSocket Endpoint

| Endpoint | Descripción |
|----------|-------------|
| `ws://localhost:8000/ws/{username}` | Conexión WebSocket para el usuario |

### Ejemplos de Mensajes WebSocket

**Cliente envía:**
```json
{
  "message": "Hola a todos!"
}
```

**Servidor envía (mensaje de chat):**
```json
{
  "type": "message",
  "username": "Juan",
  "message": "Hola a todos!",
  "timestamp": "2025-12-09T12:34:56.789Z"
}
```

**Servidor envía (usuario conectado):**
```json
{
  "type": "user_joined",
  "username": "María",
  "timestamp": "2025-12-09T12:34:56.789Z",
  "online_users": 3
}
```

**Servidor envía (usuario desconectado):**
```json
{
  "type": "user_left",
  "username": "Pedro",
  "timestamp": "2025-12-09T12:34:56.789Z",
  "online_users": 2
}
```

## Tecnologías Utilizadas

### Backend
- **FastAPI**: Framework web moderno y rápido
- **Uvicorn**: Servidor ASGI
- **WebSockets**: Protocolo de comunicación bidireccional
- **Python 3.8+**

### Frontend
- **React 18**: Biblioteca de UI
- **Vite**: Build tool y dev server
- **JavaScript ES6+**
- **CSS3**: Estilos modernos con gradientes y animaciones

## Características Técnicas

### Backend
- ✅ Gestión de conexiones WebSocket
- ✅ Broadcast de mensajes a todos los clientes
- ✅ Manejo de desconexiones
- ✅ CORS configurado para desarrollo
- ✅ Mensajes con timestamps
- ✅ Contador de usuarios en línea

### Frontend
- ✅ Hook personalizado para WebSocket
- ✅ Reconexión automática con backoff exponencial
- ✅ Indicador de estado de conexión
- ✅ Scroll automático a nuevos mensajes
- ✅ Diseño responsivo
- ✅ Validación de mensajes
- ✅ Distinción visual entre mensajes propios y de otros

## Configuración Avanzada

### Variables de Entorno (Backend)

Crea un archivo `.env` en la carpeta `backend/`:

```env
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Cambiar Puerto del Frontend

Edita `frontend/vite.config.js`:

```javascript
export default defineConfig({
  server: {
    port: 3000  // Cambiar a tu puerto preferido
  }
})
```

### Cambiar URL del WebSocket

Edita `frontend/src/hooks/useWebSocket.js`:

```javascript
const WEBSOCKET_URL = 'ws://tu-servidor:puerto/ws'
```

## Testing

### Probar el Backend con wscat

```bash
# Instalar wscat
npm install -g wscat

# Conectar al WebSocket
wscat -c ws://localhost:8000/ws/TestUser

# Enviar mensaje
> {"message": "Hola desde wscat"}
```

### Probar el Backend con curl

```bash
# Verificar estado del servidor
curl http://localhost:8000/health
```

### Probar con Postman

1. Abre Postman
2. Crea una nueva solicitud WebSocket
3. URL: `ws://localhost:8000/ws/TestUser`
4. Conecta y envía mensajes JSON

## Solución de Problemas

### El backend no inicia

**Error: `ModuleNotFoundError: No module named 'fastapi'`**
```bash
# Asegúrate de estar en el entorno virtual
source venv/bin/activate  # macOS/Linux
# o
venv\Scripts\activate     # Windows

# Reinstala las dependencias
pip install -r requirements.txt
```

**Error: Puerto 8000 ya en uso**
```bash
# Cambiar el puerto en main.py o usar:
uvicorn main:app --reload --port 8001
```

### El frontend no conecta

**Error: WebSocket connection failed**

1. Verifica que el backend esté corriendo
2. Revisa la URL del WebSocket en `useWebSocket.js`
3. Verifica que no haya problemas de CORS

**Error: Cannot find module**
```bash
# Elimina node_modules y reinstala
rm -rf node_modules package-lock.json
npm install
```

### CORS Issues

Si tienes problemas de CORS, verifica el archivo `backend/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Próximos Pasos

Mejoras que puedes implementar:

- [ ] Agregar autenticación con JWT
- [ ] Implementar salas de chat (rooms)
- [ ] Agregar persistencia de mensajes (base de datos)
- [ ] Implementar typing indicators
- [ ] Agregar emojis y markdown
- [ ] Implementar mensajes privados
- [ ] Agregar carga de archivos/imágenes
- [ ] Implementar notificaciones de escritorio
- [ ] Agregar tests unitarios e integración
- [ ] Implementar paginación de mensajes

## Recursos de Aprendizaje

📚 Lee la **[Guía Completa de WebSockets](./GUIA_WEBSOCKETS.md)** incluida en este proyecto para aprender:
- Qué son los WebSockets
- Cómo funcionan internamente
- Mejores prácticas
- Seguridad
- Escalabilidad
- Y mucho más...

## Documentación Adicional

- [FastAPI WebSockets](https://fastapi.tiangolo.com/advanced/websockets/)
- [MDN WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [React Hooks](https://react.dev/reference/react)
- [Vite Guide](https://vitejs.dev/guide/)

## Licencia

MIT

## Contacto

Si tienes preguntas o sugerencias, no dudes en contactar.

---

¡Feliz coding! 🚀
