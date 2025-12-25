# Guía Completa de WebSockets

## Índice
1. [Introducción a WebSockets](#introducción-a-websockets)
2. [Conceptos Fundamentales](#conceptos-fundamentales)
3. [Socket.io](#socketio)
4. [Patrones Comunes](#patrones-comunes)
5. [Ejemplos Prácticos](#ejemplos-prácticos)
6. [Best Practices](#best-practices)
7. [Seguridad](#seguridad)
8. [Escalabilidad](#escalabilidad)

---

## Introducción a WebSockets

### ¿Qué son WebSockets?

WebSocket es un protocolo de comunicación que proporciona **canales de comunicación bidireccional full-duplex** sobre una única conexión TCP.

**Características principales:**
- ✅ Comunicación bidireccional en tiempo real
- ✅ Baja latencia (~50ms vs 500ms+ de HTTP polling)
- ✅ Menor overhead que HTTP
- ✅ Una sola conexión persistente
- ✅ Eventos push del servidor al cliente

### WebSocket vs HTTP

| Aspecto | HTTP | WebSocket |
|---------|------|-----------|
| **Modelo** | Request/Response | Bidireccional |
| **Conexión** | Nueva por petición | Persistente |
| **Latencia** | Alta (500ms+) | Muy baja (50ms) |
| **Overhead** | Alto (headers) | Bajo |
| **Servidor → Cliente** | No nativo | ✅ Nativo |
| **Uso típico** | APIs REST | Tiempo real |

### ¿Cuándo usar WebSockets?

✅ **SÍ usar cuando:**
- Necesitas actualizaciones en tiempo real (< 1 segundo)
- Comunicación bidireccional es esencial
- Múltiples eventos por segundo
- Chat, gaming, colaboración

❌ **NO usar cuando:**
- Updates poco frecuentes (> 30 segundos)
- Solo necesitas servidor → cliente (usa SSE)
- No hay soporte WebSocket en tu infraestructura
- API REST tradicional es suficiente

---

## Conceptos Fundamentales

### 1. Handshake WebSocket

```javascript
// 1. Cliente hace upgrade request HTTP
GET /socket.io/ HTTP/1.1
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13

// 2. Servidor responde aceptando
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=

// 3. Conexión WebSocket establecida
```

### 2. Eventos del Ciclo de Vida

```javascript
// SERVIDOR
io.on('connection', (socket) => {
  console.log('Cliente conectado:', socket.id);

  socket.on('disconnect', (reason) => {
    console.log('Cliente desconectado:', reason);
  });

  socket.on('error', (error) => {
    console.error('Error:', error);
  });
});

// CLIENTE
socket.on('connect', () => {
  console.log('Conectado al servidor');
});

socket.on('disconnect', () => {
  console.log('Desconectado');
});

socket.on('connect_error', (error) => {
  console.error('Error de conexión:', error);
});
```

### 3. Emisión de Eventos

```javascript
// Cliente → Servidor
socket.emit('event-name', { data: 'value' });

// Servidor → Cliente
socket.emit('event-name', { data: 'value' });

// Servidor → Todos los clientes
io.emit('event-name', { data: 'value' });

// Servidor → Todos excepto emisor
socket.broadcast.emit('event-name', { data: 'value' });
```

---

## Socket.io

Socket.io es una biblioteca que simplifica el uso de WebSockets y proporciona fallbacks automáticos.

### Ventajas de Socket.io

1. **Fallbacks automáticos:** Long-polling si WebSocket no está disponible
2. **Reconnection:** Reconexión automática con backoff
3. **Rooms y Namespaces:** Organización de conexiones
4. **Broadcasting:** Envío a múltiples clientes
5. **Acknowledgements:** Confirmación de mensajes
6. **Binary support:** Envío de datos binarios

### Configuración Básica

**Servidor:**

```javascript
const express = require('express');
const http = require('http');
const socketIO = require('socket.io');

const app = express();
const server = http.createServer(app);
const io = socketIO(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  },
  pingTimeout: 60000,
  pingInterval: 25000
});

io.on('connection', (socket) => {
  console.log('Cliente conectado');

  socket.on('mensaje', (data) => {
    console.log('Mensaje recibido:', data);
    io.emit('mensaje', data);
  });
});

server.listen(3000);
```

**Cliente:**

```html
<script src="/socket.io/socket.io.js"></script>
<script>
  const socket = io();

  socket.on('connect', () => {
    console.log('Conectado');
  });

  socket.emit('mensaje', { text: 'Hola' });

  socket.on('mensaje', (data) => {
    console.log('Mensaje:', data);
  });
</script>
```

---

## Patrones Comunes

### 1. Broadcasting

```javascript
// A todos
io.emit('update', data);

// A todos excepto emisor
socket.broadcast.emit('update', data);

// A sala específica
io.to('room-name').emit('update', data);

// A múltiples salas
io.to('room1').to('room2').emit('update', data);
```

### 2. Rooms (Salas)

```javascript
// Unirse a sala
socket.join('room-name');

// Salir de sala
socket.leave('room-name');

// Emitir a sala
io.to('room-name').emit('message', data);

// Obtener sockets en una sala
const socketsInRoom = await io.in('room-name').fetchSockets();
```

### 3. Namespaces

```javascript
// Servidor - crear namespaces
const chatNamespace = io.of('/chat');
const adminNamespace = io.of('/admin');

chatNamespace.on('connection', (socket) => {
  console.log('Usuario en chat');
});

adminNamespace.on('connection', (socket) => {
  console.log('Admin conectado');
});

// Cliente - conectar a namespace
const chatSocket = io('/chat');
const adminSocket = io('/admin');
```

### 4. Acknowledgements

```javascript
// Cliente envía con callback
socket.emit('save-data', data, (response) => {
  if (response.status === 'ok') {
    console.log('Datos guardados');
  }
});

// Servidor responde
socket.on('save-data', (data, callback) => {
  // Guardar datos...
  callback({ status: 'ok' });
});
```

### 5. Middleware

```javascript
// Autenticación
io.use((socket, next) => {
  const token = socket.handshake.auth.token;
  if (isValidToken(token)) {
    next();
  } else {
    next(new Error('authentication error'));
  }
});

// Logging
io.use((socket, next) => {
  console.log('Nueva conexión:', socket.id);
  next();
});
```

---

## Ejemplos Prácticos

### Ejemplo 1: Chat Básico

Ver `examples/chat/` para implementación completa.

**Concepto clave:** Rooms para salas de chat separadas.

```javascript
// Usuario se une
socket.on('join-room', ({ username, room }) => {
  socket.join(room);
  socket.to(room).emit('user-joined', { username });
});

// Enviar mensaje
socket.on('send-message', ({ text }) => {
  const user = users.get(socket.id);
  io.to(user.room).emit('new-message', {
    username: user.username,
    text,
    timestamp: Date.now()
  });
});
```

### Ejemplo 2: Dashboard

Ver `examples/dashboard/` para implementación completa.

**Concepto clave:** Broadcasting periódico de datos.

```javascript
// Actualizar cada segundo
setInterval(() => {
  const metrics = generateMetrics();
  io.emit('metrics-update', metrics);
}, 1000);
```

### Ejemplo 3: Notificaciones

Ver `examples/notifications/` para implementación completa.

**Concepto clave:** Envío dirigido a usuario específico.

```javascript
// Notificar usuario específico
const user = users.get(userId);
if (user) {
  io.to(user.socketId).emit('notification', data);
}
```

---

## Best Practices

### 1. Manejo de Errores

```javascript
// Siempre manejar errores
socket.on('error', (error) => {
  console.error('Socket error:', error);
  // Notificar al usuario
  socket.emit('error', { message: 'Algo salió mal' });
});

// Try-catch en handlers
socket.on('save-data', async (data) => {
  try {
    await database.save(data);
    socket.emit('success');
  } catch (error) {
    socket.emit('error', { message: error.message });
  }
});
```

### 2. Validación de Datos

```javascript
socket.on('send-message', (data) => {
  // Validar
  if (!data.text || typeof data.text !== 'string') {
    socket.emit('error', { message: 'Mensaje inválido' });
    return;
  }

  // Sanitizar
  const text = sanitize(data.text);

  // Procesar
  broadcast(text);
});
```

### 3. Límites de Rate

```javascript
const rateLimit = new Map();

socket.on('send-message', (data) => {
  const count = rateLimit.get(socket.id) || 0;

  if (count > 10) {
    socket.emit('error', { message: 'Demasiados mensajes' });
    return;
  }

  rateLimit.set(socket.id, count + 1);
  setTimeout(() => rateLimit.delete(socket.id), 60000);

  // Procesar mensaje...
});
```

### 4. Limpieza en Desconexión

```javascript
socket.on('disconnect', () => {
  // Limpiar estado
  users.delete(socket.id);
  activeConnections.delete(socket.id);

  // Notificar a otros
  socket.to(room).emit('user-left', { userId: socket.id });

  // Cancelar timers
  clearInterval(socket.updateTimer);
});
```

---

## Seguridad

### 1. Autenticación

```javascript
// Con tokens
io.use((socket, next) => {
  const token = socket.handshake.auth.token;

  try {
    const decoded = jwt.verify(token, SECRET);
    socket.userId = decoded.userId;
    next();
  } catch (err) {
    next(new Error('Authentication error'));
  }
});
```

### 2. Autorización

```javascript
socket.on('delete-message', async (messageId) => {
  const message = await getMessage(messageId);

  // Verificar permisos
  if (message.authorId !== socket.userId) {
    socket.emit('error', { message: 'Sin permisos' });
    return;
  }

  await deleteMessage(messageId);
});
```

### 3. CORS

```javascript
const io = socketIO(server, {
  cors: {
    origin: "https://tu-dominio.com",
    methods: ["GET", "POST"],
    credentials: true
  }
});
```

### 4. Sanitización

```javascript
const sanitizeHtml = require('sanitize-html');

socket.on('send-message', (data) => {
  const clean = sanitizeHtml(data.text, {
    allowedTags: [],
    allowedAttributes: {}
  });

  broadcast(clean);
});
```

---

## Escalabilidad

### 1. Múltiples Servidores (Redis Adapter)

```javascript
const redis = require('socket.io-redis');

io.adapter(redis({
  host: 'localhost',
  port: 6379
}));

// Ahora puedes tener múltiples instancias
// y los eventos se sincronizarán vía Redis
```

### 2. Load Balancing

**Nginx config:**

```nginx
upstream socketio {
  ip_hash;  # Sticky sessions
  server backend1:3000;
  server backend2:3000;
  server backend3:3000;
}

server {
  listen 80;

  location /socket.io/ {
    proxy_pass http://socketio;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
  }
}
```

### 3. Monitoreo

```javascript
// Estadísticas
setInterval(() => {
  console.log({
    connections: io.sockets.sockets.size,
    rooms: io.sockets.adapter.rooms.size,
    memory: process.memoryUsage()
  });
}, 30000);
```

---

## Troubleshooting

### Problema: Cliente no se conecta

**Solución:**
1. Verificar CORS
2. Verificar URL correcta
3. Ver consola del navegador
4. Verificar firewall/proxy

### Problema: Desconexiones frecuentes

**Solución:**
```javascript
const io = socketIO(server, {
  pingTimeout: 60000,    // Aumentar timeout
  pingInterval: 25000
});
```

### Problema: Alto uso de memoria

**Solución:**
- Limitar historial de mensajes
- Implementar limpieza periódica
- Usar Redis para persistencia

---

## Recursos Adicionales

- [Socket.io Docs](https://socket.io/docs/)
- [WebSocket RFC](https://tools.ietf.org/html/rfc6455)
- [MDN WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)

---

¡Explora los ejemplos en la carpeta `examples/` para ver estos conceptos en acción!
