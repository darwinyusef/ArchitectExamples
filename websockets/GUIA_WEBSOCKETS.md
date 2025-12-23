# Guía Completa de WebSockets

## Índice
1. [¿Qué son los WebSockets?](#qué-son-los-websockets)
2. [Ventajas y Desventajas](#ventajas-y-desventajas)
3. [Diferencias con HTTP](#diferencias-con-http)
4. [Casos de Uso](#casos-de-uso)
5. [Cómo Funcionan](#cómo-funcionan)
6. [Protocolo WebSocket](#protocolo-websocket)
7. [Implementación Backend (FastAPI)](#implementación-backend-fastapi)
8. [Implementación Frontend (React)](#implementación-frontend-react)
9. [Mejores Prácticas](#mejores-prácticas)
10. [Manejo de Errores](#manejo-de-errores)
11. [Seguridad](#seguridad)
12. [Escalabilidad](#escalabilidad)

---

## ¿Qué son los WebSockets?

WebSocket es un **protocolo de comunicación bidireccional y full-duplex** sobre una única conexión TCP. Permite la comunicación en tiempo real entre un cliente y un servidor.

### Características principales:
- **Comunicación bidireccional**: Cliente y servidor pueden enviar datos simultáneamente
- **Conexión persistente**: Una vez establecida, la conexión permanece abierta
- **Baja latencia**: Ideal para aplicaciones en tiempo real
- **Menor overhead**: Comparado con HTTP polling

---

## Ventajas y Desventajas

### ✅ Ventajas

1. **Comunicación en tiempo real**
   - Actualización instantánea de datos
   - Sin necesidad de polling

2. **Eficiencia**
   - Menor uso de ancho de banda
   - Reduce la carga del servidor

3. **Bidireccionalidad**
   - El servidor puede enviar datos sin que el cliente lo solicite
   - Push notifications nativas

4. **Menor latencia**
   - No hay overhead de establecer conexión en cada petición
   - Respuestas más rápidas

### ❌ Desventajas

1. **Complejidad**
   - Más complejo de implementar que HTTP
   - Requiere manejo de estado de conexión

2. **Escalabilidad**
   - Las conexiones persistentes consumen recursos
   - Requiere estrategias específicas para escalar

3. **Compatibilidad**
   - Algunos firewalls y proxies pueden bloquear WebSockets
   - Requiere soporte en navegadores antiguos

4. **Debugging**
   - Más difícil de debuggear que HTTP REST
   - Herramientas menos maduras

---

## Diferencias con HTTP

| Característica | HTTP | WebSocket |
|---------------|------|-----------|
| **Tipo de conexión** | Sin estado (stateless) | Con estado (stateful) |
| **Comunicación** | Unidireccional (request-response) | Bidireccional (full-duplex) |
| **Overhead** | Alto (headers en cada request) | Bajo (después del handshake) |
| **Latencia** | Mayor | Menor |
| **Uso de recursos** | Menor (conexiones cortas) | Mayor (conexiones persistentes) |
| **Protocolo** | HTTP/HTTPS | WS/WSS |
| **Casos de uso** | APIs REST, páginas web | Chat, juegos, datos en tiempo real |

### Ejemplo visual de comunicación:

**HTTP:**
```
Cliente → Request → Servidor
Cliente ← Response ← Servidor
Cliente → Request → Servidor
Cliente ← Response ← Servidor
```

**WebSocket:**
```
Cliente → Handshake → Servidor
Cliente ↔ Mensajes ↔ Servidor
Cliente ↔ Mensajes ↔ Servidor
Cliente ↔ Mensajes ↔ Servidor
```

---

## Casos de Uso

### 1. Aplicaciones de Chat
- Mensajería instantánea
- Chat en vivo de soporte
- Salas de chat grupales

### 2. Aplicaciones Colaborativas
- Editores de código en tiempo real (como Google Docs)
- Pizarras virtuales compartidas
- Herramientas de diseño colaborativo

### 3. Gaming
- Juegos multijugador en tiempo real
- Sincronización de estado de juego
- Chat in-game

### 4. Datos Financieros
- Cotizaciones de bolsa en tiempo real
- Gráficos de trading actualizados
- Alertas de precio

### 5. Notificaciones
- Notificaciones push
- Actualizaciones de estado
- Alertas en tiempo real

### 6. Monitoreo
- Dashboards en tiempo real
- Logs en vivo
- Métricas de sistema

### 7. IoT
- Control de dispositivos
- Telemetría en tiempo real
- Sensores y actuadores

---

## Cómo Funcionan

### 1. Handshake Inicial (Upgrade de HTTP a WebSocket)

```http
GET /ws HTTP/1.1
Host: example.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13
```

**Respuesta del servidor:**
```http
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
```

### 2. Conexión Establecida
- La conexión HTTP se "actualiza" a WebSocket
- La conexión TCP permanece abierta
- Ambas partes pueden enviar mensajes

### 3. Intercambio de Mensajes
- Datos encapsulados en frames
- Bajo overhead (2-14 bytes por frame)
- Soporte para texto y binario

### 4. Cierre de Conexión
- Cualquier parte puede iniciar el cierre
- Handshake de cierre para finalizar limpiamente

---

## Protocolo WebSocket

### Estados de la Conexión

```javascript
WebSocket.CONNECTING  // 0 - Conexión en proceso
WebSocket.OPEN        // 1 - Conexión establecida
WebSocket.CLOSING     // 2 - Conexión cerrándose
WebSocket.CLOSED      // 3 - Conexión cerrada
```

### Tipos de Frames

1. **Text Frame**: Datos de texto UTF-8
2. **Binary Frame**: Datos binarios
3. **Close Frame**: Cierre de conexión
4. **Ping Frame**: Keep-alive
5. **Pong Frame**: Respuesta a ping

### Estructura de un Frame

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-------+-+-------------+-------------------------------+
|F|R|R|R| opcode|M| Payload len |    Extended payload length    |
|I|S|S|S|  (4)  |A|     (7)     |             (16/64)           |
|N|V|V|V|       |S|             |   (if payload len==126/127)   |
| |1|2|3|       |K|             |                               |
+-+-+-+-+-------+-+-------------+ - - - - - - - - - - - - - - - +
|     Extended payload length continued, if payload len == 127  |
+ - - - - - - - - - - - - - - - +-------------------------------+
|                               |Masking-key, if MASK set to 1  |
+-------------------------------+-------------------------------+
| Masking-key (continued)       |          Payload Data         |
+-------------------------------- - - - - - - - - - - - - - - - +
:                     Payload Data continued ...                :
+ - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - +
|                     Payload Data continued ...                |
+---------------------------------------------------------------+
```

---

## Implementación Backend (FastAPI)

### Configuración Básica

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Message: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

### Manejo de JSON

```python
import json

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            # Recibir JSON
            data = await websocket.receive_json()

            # Procesar datos
            response = {
                "client_id": client_id,
                "message": data.get("message"),
                "timestamp": datetime.now().isoformat()
            }

            # Enviar JSON
            await manager.broadcast(response)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

### Autenticación

```python
from fastapi import WebSocket, HTTPException, Depends

async def get_token(websocket: WebSocket):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008)  # Policy Violation
        raise HTTPException(status_code=401)
    return token

@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Depends(get_token)
):
    # Verificar token
    user = verify_token(token)
    if not user:
        await websocket.close(code=1008)
        return

    await manager.connect(websocket, user)
    # ... resto del código
```

---

## Implementación Frontend (React)

### Hook Personalizado para WebSocket

```javascript
import { useState, useEffect, useRef, useCallback } from 'react'

function useWebSocket(url, username) {
  const [messages, setMessages] = useState([])
  const [isConnected, setIsConnected] = useState(false)
  const ws = useRef(null)

  useEffect(() => {
    // Crear conexión
    ws.current = new WebSocket(`${url}/${username}`)

    ws.current.onopen = () => {
      console.log('Connected')
      setIsConnected(true)
    }

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data)
      setMessages(prev => [...prev, data])
    }

    ws.current.onerror = (error) => {
      console.error('WebSocket error:', error)
    }

    ws.current.onclose = () => {
      console.log('Disconnected')
      setIsConnected(false)
    }

    // Cleanup
    return () => {
      ws.current?.close()
    }
  }, [url, username])

  const sendMessage = useCallback((message) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({ message }))
    }
  }, [])

  return { messages, sendMessage, isConnected }
}

export default useWebSocket
```

### Componente de Chat

```javascript
import { useState } from 'react'
import useWebSocket from './hooks/useWebSocket'

function Chat({ username }) {
  const [input, setInput] = useState('')
  const { messages, sendMessage, isConnected } = useWebSocket(
    'ws://localhost:8000/ws',
    username
  )

  const handleSubmit = (e) => {
    e.preventDefault()
    if (input.trim()) {
      sendMessage(input)
      setInput('')
    }
  }

  return (
    <div>
      <div>Status: {isConnected ? 'Connected' : 'Disconnected'}</div>

      <div className="messages">
        {messages.map((msg, i) => (
          <div key={i}>
            <strong>{msg.username}:</strong> {msg.message}
          </div>
        ))}
      </div>

      <form onSubmit={handleSubmit}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={!isConnected}
        />
        <button type="submit" disabled={!isConnected}>Send</button>
      </form>
    </div>
  )
}
```

### Reconexión Automática

```javascript
function useWebSocket(url, username) {
  const [isConnected, setIsConnected] = useState(false)
  const ws = useRef(null)
  const reconnectTimeout = useRef(null)
  const reconnectAttempts = useRef(0)

  const connect = useCallback(() => {
    ws.current = new WebSocket(`${url}/${username}`)

    ws.current.onopen = () => {
      setIsConnected(true)
      reconnectAttempts.current = 0
    }

    ws.current.onclose = () => {
      setIsConnected(false)

      // Reconectar con backoff exponencial
      const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000)
      reconnectAttempts.current++

      reconnectTimeout.current = setTimeout(() => {
        console.log('Reconnecting...')
        connect()
      }, delay)
    }
  }, [url, username])

  useEffect(() => {
    connect()
    return () => {
      clearTimeout(reconnectTimeout.current)
      ws.current?.close()
    }
  }, [connect])

  // ... resto del código
}
```

---

## Mejores Prácticas

### 1. Manejo de Estado de Conexión

```javascript
// Siempre verificar el estado antes de enviar
if (ws.readyState === WebSocket.OPEN) {
  ws.send(data)
}
```

### 2. Heartbeat / Keep-Alive

**Backend (FastAPI):**
```python
import asyncio

async def send_heartbeat(websocket: WebSocket):
    while True:
        try:
            await asyncio.sleep(30)  # Cada 30 segundos
            await websocket.send_json({"type": "ping"})
        except:
            break
```

**Frontend (React):**
```javascript
useEffect(() => {
  const interval = setInterval(() => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({ type: 'ping' }))
    }
  }, 30000)

  return () => clearInterval(interval)
}, [])
```

### 3. Validación de Mensajes

```python
from pydantic import BaseModel, validator

class Message(BaseModel):
    type: str
    content: str

    @validator('content')
    def content_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Content cannot be empty')
        return v

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    try:
        data = await websocket.receive_json()
        message = Message(**data)  # Validar
        # Procesar mensaje validado
    except ValidationError as e:
        await websocket.send_json({"error": str(e)})
```

### 4. Limitación de Tasa (Rate Limiting)

```python
from collections import defaultdict
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, max_messages=10, window=60):
        self.max_messages = max_messages
        self.window = timedelta(seconds=window)
        self.messages = defaultdict(list)

    def is_allowed(self, client_id: str) -> bool:
        now = datetime.now()
        # Limpiar mensajes antiguos
        self.messages[client_id] = [
            msg_time for msg_time in self.messages[client_id]
            if now - msg_time < self.window
        ]

        if len(self.messages[client_id]) >= self.max_messages:
            return False

        self.messages[client_id].append(now)
        return True

limiter = RateLimiter()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()

            if not limiter.is_allowed(client_id):
                await websocket.send_json({
                    "error": "Rate limit exceeded"
                })
                continue

            # Procesar mensaje
    except WebSocketDisconnect:
        pass
```

### 5. Compresión de Mensajes

```python
import json
import gzip

async def send_compressed(websocket: WebSocket, data: dict):
    json_str = json.dumps(data)
    if len(json_str) > 1024:  # Comprimir si es grande
        compressed = gzip.compress(json_str.encode())
        await websocket.send_bytes(compressed)
    else:
        await websocket.send_json(data)
```

---

## Manejo de Errores

### Códigos de Cierre WebSocket

| Código | Significado | Descripción |
|--------|-------------|-------------|
| 1000 | Normal Closure | Cierre normal |
| 1001 | Going Away | Endpoint desapareciendo |
| 1002 | Protocol Error | Error de protocolo |
| 1003 | Unsupported Data | Datos no soportados |
| 1006 | Abnormal Closure | Cierre anormal (sin frame) |
| 1007 | Invalid Payload | Datos inválidos |
| 1008 | Policy Violation | Violación de política |
| 1009 | Message Too Big | Mensaje muy grande |
| 1011 | Internal Error | Error interno del servidor |

### Manejo de Errores en Backend

```python
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    try:
        await websocket.accept()

        while True:
            try:
                data = await websocket.receive_text()
                # Procesar datos

            except json.JSONDecodeError:
                await websocket.send_json({
                    "error": "Invalid JSON"
                })

            except ValueError as e:
                await websocket.send_json({
                    "error": str(e)
                })

    except WebSocketDisconnect:
        print(f"Client disconnected")

    except Exception as e:
        print(f"Error: {e}")
        await websocket.close(code=1011)
```

### Manejo de Errores en Frontend

```javascript
ws.onerror = (error) => {
  console.error('WebSocket error:', error)
  setError('Connection error occurred')
}

ws.onclose = (event) => {
  console.log('WebSocket closed:', event.code, event.reason)

  switch(event.code) {
    case 1000:
      console.log('Normal closure')
      break
    case 1006:
      console.log('Abnormal closure - attempting reconnect')
      reconnect()
      break
    case 1008:
      console.log('Policy violation - please check authentication')
      break
    default:
      console.log('Connection closed with code:', event.code)
  }
}
```

---

## Seguridad

### 1. Usar WSS (WebSocket Secure)

```javascript
// Producción - siempre usar wss://
const ws = new WebSocket('wss://example.com/ws')
```

### 2. Autenticación con Token

```javascript
// Frontend
const token = localStorage.getItem('auth_token')
const ws = new WebSocket(`wss://example.com/ws?token=${token}`)
```

```python
# Backend
from fastapi import WebSocket, HTTPException

async def verify_token(token: str):
    # Verificar JWT o token de sesión
    user = decode_jwt(token)
    if not user:
        raise HTTPException(status_code=401)
    return user

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str):
    user = await verify_token(token)
    await websocket.accept()
    # ...
```

### 3. Validación de Origen (CORS)

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 4. Sanitización de Inputs

```python
import bleach

def sanitize_message(message: str) -> str:
    return bleach.clean(message, strip=True)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    data = await websocket.receive_text()
    clean_data = sanitize_message(data)
    # Procesar mensaje limpio
```

### 5. Límites de Tamaño de Mensaje

```python
MAX_MESSAGE_SIZE = 10 * 1024  # 10KB

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    try:
        data = await websocket.receive_text()

        if len(data) > MAX_MESSAGE_SIZE:
            await websocket.send_json({
                "error": "Message too large"
            })
            await websocket.close(code=1009)
            return

        # Procesar mensaje
    except:
        pass
```

---

## Escalabilidad

### 1. Redis Pub/Sub para Múltiples Servidores

```python
import redis.asyncio as redis

class RedisConnectionManager:
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379)
        self.pubsub = self.redis.pubsub()

    async def subscribe(self, channel: str):
        await self.pubsub.subscribe(channel)

    async def publish(self, channel: str, message: dict):
        await self.redis.publish(channel, json.dumps(message))

    async def listen(self):
        async for message in self.pubsub.listen():
            if message['type'] == 'message':
                yield json.loads(message['data'])

redis_manager = RedisConnectionManager()

@app.websocket("/ws/{room}")
async def websocket_endpoint(websocket: WebSocket, room: str):
    await websocket.accept()
    await redis_manager.subscribe(f"room:{room}")

    async def receive_messages():
        async for message in redis_manager.listen():
            await websocket.send_json(message)

    async def send_messages():
        while True:
            data = await websocket.receive_json()
            await redis_manager.publish(f"room:{room}", data)

    # Ejecutar ambas tareas concurrentemente
    await asyncio.gather(
        receive_messages(),
        send_messages()
    )
```

### 2. Load Balancing

**Nginx Configuration:**
```nginx
upstream websocket {
    ip_hash;  # Importante para sticky sessions
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}

server {
    location /ws {
        proxy_pass http://websocket;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. Monitoring y Métricas

```python
from prometheus_client import Counter, Gauge

# Métricas
websocket_connections = Gauge(
    'websocket_connections',
    'Number of active WebSocket connections'
)
messages_sent = Counter(
    'websocket_messages_sent',
    'Total messages sent'
)
messages_received = Counter(
    'websocket_messages_received',
    'Total messages received'
)

class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        websocket_connections.inc()

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        websocket_connections.dec()

    async def broadcast(self, message: dict):
        messages_sent.inc(len(self.active_connections))
        for connection in self.active_connections:
            await connection.send_json(message)
```

### 4. Límite de Conexiones por Usuario

```python
from collections import defaultdict

class ConnectionManager:
    def __init__(self):
        self.active_connections = []
        self.user_connections = defaultdict(int)
        self.max_connections_per_user = 5

    async def connect(self, websocket: WebSocket, user_id: str):
        if self.user_connections[user_id] >= self.max_connections_per_user:
            await websocket.close(code=1008, reason="Too many connections")
            return False

        await websocket.accept()
        self.active_connections.append(websocket)
        self.user_connections[user_id] += 1
        return True

    def disconnect(self, websocket: WebSocket, user_id: str):
        self.active_connections.remove(websocket)
        self.user_connections[user_id] -= 1
```

---

## Testing

### Backend Tests (pytest)

```python
from fastapi.testclient import TestClient

def test_websocket():
    client = TestClient(app)

    with client.websocket_connect("/ws/testuser") as websocket:
        # Enviar mensaje
        websocket.send_json({"message": "Hello"})

        # Recibir respuesta
        data = websocket.receive_json()
        assert data["username"] == "testuser"
        assert data["message"] == "Hello"

def test_websocket_disconnect():
    client = TestClient(app)

    with client.websocket_connect("/ws/user1") as ws1:
        with client.websocket_connect("/ws/user2") as ws2:
            # user1 envía mensaje
            ws1.send_json({"message": "Hi"})

            # user2 recibe el mensaje
            data = ws2.receive_json()
            assert data["message"] == "Hi"
```

### Frontend Tests (Jest + React Testing Library)

```javascript
import { renderHook, act } from '@testing-library/react-hooks'
import useWebSocket from './useWebSocket'

// Mock WebSocket
global.WebSocket = jest.fn(() => ({
  send: jest.fn(),
  close: jest.fn(),
  addEventListener: jest.fn()
}))

test('connects to WebSocket', () => {
  const { result } = renderHook(() =>
    useWebSocket('ws://localhost:8000/ws', 'testuser')
  )

  expect(result.current.isConnected).toBe(false)

  // Simular conexión
  act(() => {
    result.current.ws.current.onopen()
  })

  expect(result.current.isConnected).toBe(true)
})
```

---

## Recursos Adicionales

### Documentación Oficial
- [RFC 6455 - The WebSocket Protocol](https://tools.ietf.org/html/rfc6455)
- [MDN WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [FastAPI WebSockets](https://fastapi.tiangolo.com/advanced/websockets/)

### Herramientas
- [Postman WebSocket Testing](https://www.postman.com/)
- [wscat](https://github.com/websockets/wscat) - CLI para testing
- [WebSocket King](https://websocketking.com/) - Cliente de testing en navegador

### Libraries
- **Python**: `websockets`, `python-socketio`
- **JavaScript**: `socket.io-client`, `ws`
- **React**: `use-websocket`, `react-use-websocket`

---

## Conclusión

WebSockets son una tecnología poderosa para aplicaciones en tiempo real. Al seguir las mejores prácticas de esta guía, podrás implementar soluciones robustas, seguras y escalables.

### Checklist de Implementación

- [ ] Implementar autenticación y autorización
- [ ] Agregar manejo de errores robusto
- [ ] Implementar reconexión automática
- [ ] Agregar heartbeat/keep-alive
- [ ] Validar y sanitizar todos los inputs
- [ ] Implementar rate limiting
- [ ] Configurar CORS correctamente
- [ ] Usar WSS en producción
- [ ] Implementar logging y monitoring
- [ ] Escribir tests
- [ ] Documentar la API
- [ ] Planear estrategia de escalabilidad
