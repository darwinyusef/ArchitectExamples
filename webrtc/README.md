# WebRTC + WebSocket CRUD con FastAPI

Aplicación completa que demuestra el uso de **concurrencia** y **paralelismo** en Python usando FastAPI, WebSockets y WebRTC.

## Características Principales

### 1. CRUD Completo con Concurrencia
- ✅ Operaciones asíncronas (Create, Read, Update, Delete)
- ✅ Base de datos SQLite con SQLAlchemy async
- ✅ Operaciones bulk para crear/actualizar múltiples items en paralelo
- ✅ Background tasks para procesamiento asíncrono

### 2. WebSocket para Señalización
- ✅ Servidor WebSocket con múltiples rooms concurrentes
- ✅ Gestión de múltiples conexiones simultáneas
- ✅ Broadcast de mensajes a todos los peers en un room
- ✅ Thread-safe operations con asyncio.Lock

### 3. WebRTC para Comunicación P2P
- ✅ Conexiones peer-to-peer directas
- ✅ Data channels para mensajería P2P
- ✅ Señalización completa (offer/answer/ICE candidates)
- ✅ Soporte para múltiples peers en la misma sala

### 4. Concurrencia y Paralelismo
- ✅ `asyncio` para operaciones I/O concurrentes
- ✅ `asyncio.gather()` para ejecutar múltiples tareas en paralelo
- ✅ `BackgroundTasks` para procesamiento en background
- ✅ Async database sessions para múltiples queries concurrentes

## Arquitectura del Proyecto

```
grtc/
├── app/
│   ├── models/
│   │   ├── database.py       # Modelos SQLAlchemy y configuración DB
│   │   └── schemas.py        # Schemas Pydantic para validación
│   ├── routers/
│   │   ├── items.py          # Endpoints CRUD REST
│   │   └── websocket.py      # WebSocket endpoints
│   └── services/
│       ├── crud_service.py   # Lógica de negocio CRUD
│       └── websocket_service.py  # Gestor de conexiones WebSocket
├── static/
│   ├── app.js               # Cliente JavaScript con WebRTC
│   └── style.css            # Estilos CSS
├── templates/
│   └── index.html           # Interfaz web
├── main.py                  # Aplicación FastAPI principal
├── requirements.txt         # Dependencias Python
└── README.md               # Este archivo
```

## Instalación

### 1. Clonar el repositorio o usar el directorio actual

```bash
cd grtc
```

### 2. Crear entorno virtual

```bash
python -m venv venv

# En Linux/Mac
source venv/bin/activate

# En Windows
venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

## Ejecución

### Opción 1: Local

```bash
python main.py
```

O con uvicorn directamente:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

El servidor estará disponible en: `http://localhost:8001`

### Opción 2: Docker (Recomendado) 🐳

```bash
# Solo backend
docker-compose up -d

# Con Nginx
docker-compose --profile with-nginx up -d

# Con clientes simulados (testing)
docker-compose --profile with-clients up -d

# Todo junto
docker-compose --profile with-nginx --profile with-clients up -d
```

**Servicios disponibles:**
- Backend: http://localhost:8001
- Nginx: http://localhost (si usas profile with-nginx)
- Cliente A VNC: http://localhost:7900 (si usas profile with-clients)
- Cliente B VNC: http://localhost:7901 (si usas profile with-clients)

Ver **[DOCKER_DEPLOY.md](./DOCKER_DEPLOY.md)** para más detalles.

## Uso de la Aplicación

### Interfaz Web

Abre tu navegador en `http://localhost:8000` para acceder a la interfaz completa.

### Operaciones CRUD

#### Crear un Item
- Completa el formulario con título, descripción y status
- Click en "Crear Item"

#### Crear Items en Bulk (Concurrencia)
- Click en "Crear 5 Items (Bulk)"
- Se crearán 5 items en paralelo usando `asyncio.gather()`

#### Listar Items
- Click en "Cargar Items"
- Filtra por status si lo deseas

#### Actualizar Items en Bulk
- Carga items primero
- Click en "Actualizar Status (Bulk)"
- Se actualizarán múltiples items en paralelo

#### Actualizar/Eliminar Item Individual
- Usa los botones en cada item de la lista

### WebRTC y WebSocket

#### Conectar a un Room
1. Ingresa un Room ID (ej: "room1")
2. Click en "Conectar al Room"
3. El WebSocket se conecta y recibes un Peer ID único

#### Abrir en Múltiples Pestañas
Para ver la comunicación P2P:
1. Abre `http://localhost:8000` en 2-3 pestañas
2. Conéctalas al mismo Room ID
3. Los peers se detectarán automáticamente
4. Se establecerán conexiones WebRTC P2P

#### Enviar Mensajes Broadcast
- Escribe un mensaje
- Click en "Enviar"
- Todos los peers en el room recibirán el mensaje

## API REST Endpoints

### Items CRUD

```bash
# Crear item
POST /api/items/
Content-Type: application/json
{
  "title": "Mi Item",
  "description": "Descripción",
  "status": "active"
}

# Listar items
GET /api/items/?skip=0&limit=100&status=active

# Obtener item
GET /api/items/{item_id}

# Actualizar item
PUT /api/items/{item_id}
Content-Type: application/json
{
  "title": "Nuevo título",
  "status": "inactive"
}

# Eliminar item
DELETE /api/items/{item_id}

# Crear múltiples items (concurrencia)
POST /api/items/bulk
Content-Type: application/json
[
  {"title": "Item 1", "status": "active"},
  {"title": "Item 2", "status": "pending"}
]

# Actualizar status en bulk (paralelismo)
PATCH /api/items/bulk/status?new_status=active
Content-Type: application/json
[1, 2, 3, 4, 5]
```

### WebSocket

```javascript
// Conectar a un room
const ws = new WebSocket('ws://localhost:8000/ws/room1?peer_id=peer-123');

// Enviar señal WebRTC
ws.send(JSON.stringify({
  type: 'offer',
  target_peer_id: 'peer-456',
  offer: rtcOffer
}));

// Broadcast
ws.send(JSON.stringify({
  type: 'broadcast',
  data: 'Mensaje para todos'
}));
```

### Rooms

```bash
# Obtener rooms activos
GET /rooms

# Obtener peers en un room
GET /rooms/{room_id}/peers
```

## Conceptos de Concurrencia Implementados

### 1. Async/Await
```python
async def create_item(db: AsyncSession, item_data: ItemCreate):
    new_item = Item(...)
    db.add(new_item)
    await db.commit()  # Operación I/O no bloqueante
    return new_item
```

### 2. Operaciones en Paralelo con asyncio.gather()
```python
# Crear múltiples items concurrentemente
await asyncio.gather(*[db.refresh(item) for item in items])
```

### 3. Background Tasks
```python
@app.post("/{item_id}/process")
async def process_item(item_id: int, background_tasks: BackgroundTasks):
    background_tasks.add_task(long_running_task, item_id)
    return {"status": "processing"}
```

### 4. Thread-Safe Operations
```python
async with self.lock:
    self.active_connections[room_id][peer_id] = websocket
```

### 5. Conexiones WebSocket Concurrentes
El servidor puede manejar múltiples conexiones WebSocket simultáneamente, cada una en su propio contexto asíncrono.

## Testing con Curl

### Crear item
```bash
curl -X POST http://localhost:8000/api/items/ \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Item","description":"Testing","status":"active"}'
```

### Listar items
```bash
curl http://localhost:8000/api/items/
```

### Crear items en bulk
```bash
curl -X POST http://localhost:8000/api/items/bulk \
  -H "Content-Type: application/json" \
  -d '[
    {"title":"Item 1","status":"active"},
    {"title":"Item 2","status":"pending"},
    {"title":"Item 3","status":"inactive"}
  ]'
```

## Tecnologías Utilizadas

- **FastAPI**: Framework web moderno y rápido
- **SQLAlchemy**: ORM con soporte async
- **aiosqlite**: Driver SQLite asíncrono
- **WebSockets**: Comunicación bidireccional en tiempo real
- **WebRTC**: Comunicación peer-to-peer
- **Pydantic**: Validación de datos
- **Asyncio**: Biblioteca de concurrencia de Python
- **Uvicorn**: Servidor ASGI de alto rendimiento

## Ventajas de la Concurrencia y Paralelismo

1. **Mayor throughput**: Múltiples operaciones I/O simultáneas
2. **Mejor responsiveness**: No se bloquea el event loop
3. **Escalabilidad**: Maneja múltiples clientes concurrentemente
4. **Eficiencia**: Mejor uso de recursos del sistema
5. **Real-time capabilities**: WebSocket y WebRTC para comunicación instantánea

## Próximos Pasos / Mejoras

- [ ] Agregar autenticación con JWT
- [ ] Implementar Redis para gestión de estado compartido
- [ ] Agregar rate limiting
- [ ] Implementar retry logic para operaciones fallidas
- [ ] Agregar métricas y monitoring
- [ ] Testing unitario y de integración
- [ ] Containerización con Docker
- [ ] Deploy en producción con HTTPS

## Licencia

MIT

## Autor

Proyecto de demostración de concurrencia y paralelismo con FastAPI, WebSocket y WebRTC.
