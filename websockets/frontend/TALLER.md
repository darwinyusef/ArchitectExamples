# Taller Práctico de WebSockets

## Objetivo
Aplicar los conceptos de WebSockets mediante ejercicios progresivos sobre los ejemplos existentes.

---

## Preparación

```bash
cd websockets
npm install
```

---

## Ejercicios Nivel Básico

### Ejercicio 1: Modificar el Chat - Agregar Timestamps Formateados

**Objetivo:** Mejorar la visualización de fechas en el chat.

**Archivo:** `examples/chat/public/chat.js`

**Tarea:**
1. Modifica la función `formatTime()` para mostrar también la fecha si el mensaje es de otro día
2. Formato: "Hoy 10:30 AM" o "Ayer 10:30 AM" o "15/12 10:30 AM"

**Pista:**
```javascript
function formatTime(timestamp) {
  const date = new Date(timestamp);
  const now = new Date();
  const diff = now.getDate() - date.getDate();

  // Tu código aquí
}
```

---

### Ejercicio 2: Dashboard - Agregar Nueva Métrica

**Objetivo:** Agregar una nueva tarjeta de métrica al dashboard.

**Archivos:**
- `examples/dashboard/server.js`
- `examples/dashboard/public/index.html`
- `examples/dashboard/public/dashboard.js`

**Tareas:**
1. Agregar métrica de "Tasa de Rebote" (40-70%) en el servidor
2. Crear tarjeta en el HTML
3. Actualizar en el cliente

---

### Ejercicio 3: Notificaciones - Sonido al Recibir

**Objetivo:** Reproducir sonido cuando llega una notificación.

**Archivo:** `examples/notifications/public/notifications.js`

**Tarea:**
1. Usar Web Audio API para reproducir un sonido
2. Agregar opción para silenciar notificaciones

**Pista:**
```javascript
const audio = new Audio('/notification.mp3');
socket.on('notification', (data) => {
  audio.play();
  // ...
});
```

---

## Ejercicios Nivel Intermedio

### Ejercicio 4: Chat - Comandos de Slash

**Objetivo:** Implementar comandos estilo Discord (/help, /clear, /private).

**Archivo:** `examples/chat/public/chat.js`

**Comandos a implementar:**
- `/help` - Mostrar ayuda
- `/clear` - Limpiar mensajes localmente
- `/private @usuario mensaje` - Mensaje privado
- `/list` - Listar usuarios

**Ejemplo:**
```javascript
if (text.startsWith('/')) {
  const [command, ...args] = text.slice(1).split(' ');

  switch(command) {
    case 'help':
      displaySystemMessage('Comandos: /help, /clear, /private');
      break;
    // ...
  }
  return; // No enviar al servidor
}
```

---

### Ejercicio 5: Dashboard - Exportar Datos

**Objetivo:** Agregar botón para exportar métricas a CSV.

**Archivo:** `examples/dashboard/public/dashboard.js`

**Tareas:**
1. Crear botón "Exportar CSV"
2. Función para convertir datos a CSV
3. Descargar archivo automáticamente

**Pista:**
```javascript
function exportToCSV() {
  const csv = metricsHistory.timestamps.map((time, i) => {
    return `${time},${metricsHistory.users[i]},${metricsHistory.revenue[i]}`;
  }).join('\n');

  const blob = new Blob([csv], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'metrics.csv';
  a.click();
}
```

---

### Ejercicio 6: Chat - Persistencia con LocalStorage

**Objetivo:** Guardar historial de mensajes en localStorage.

**Archivo:** `examples/chat/public/chat.js`

**Tareas:**
1. Guardar mensajes en localStorage
2. Cargar al reconectar
3. Límite de 100 mensajes

---

## Ejercicios Nivel Avanzado

### Ejercicio 7: Chat - Reacciones a Mensajes

**Objetivo:** Agregar reacciones estilo Slack (👍, ❤️, 😂).

**Archivos:**
- `examples/chat/server.js`
- `examples/chat/public/`

**Tareas:**
1. Agregar UI de reacciones en cada mensaje
2. Evento `add-reaction` en servidor
3. Broadcast de reacciones
4. Contador por reacción

**Estructura de datos:**
```javascript
message: {
  id: 'msg-123',
  text: 'Hola',
  reactions: {
    '👍': ['user1', 'user2'],
    '❤️': ['user3']
  }
}
```

---

### Ejercicio 8: Dashboard - Alertas Configurables

**Objetivo:** Permitir configurar umbrales de alertas.

**Tareas:**
1. UI para configurar umbrales (ej: CPU > 80%)
2. Validar en servidor
3. Emitir alerta solo si se supera umbral
4. Persistir configuración

---

### Ejercicio 9: Sistema de Presencia

**Objetivo:** Mostrar estado "Online/Away/Busy" de usuarios.

**Archivos:** Crear nuevo ejemplo `examples/presence/`

**Tareas:**
1. Usuario puede cambiar su estado
2. Broadcast de cambios de estado
3. Lista de usuarios con su estado
4. Auto-away después de 5 minutos inactivo

**Eventos a implementar:**
- `set-status` - Cambiar estado
- `status-changed` - Broadcast
- `get-all-status` - Obtener todos

---

### Ejercicio 10: Chat con Cifrado E2E

**Objetivo:** Implementar cifrado básico de mensajes.

**Usar:** Web Crypto API

**Tareas:**
1. Generar par de claves por usuario
2. Intercambiar claves públicas
3. Cifrar mensajes antes de enviar
4. Descifrar al recibir

**Nota:** Este es un ejercicio educativo. En producción usar librerías especializadas.

---

## Ejercicios Desafío

### Desafío 1: Juego Multiplayer - Piedra, Papel o Tijera

**Crear:** `examples/game/`

**Características:**
- Matchmaking automático
- Rooms para cada partida
- Contador de puntos
- Múltiples partidas simultáneas

---

### Desafío 2: Pizarra Colaborativa

**Crear:** `examples/whiteboard/`

**Características:**
- Canvas HTML5
- Dibujo en tiempo real
- Múltiples usuarios simultáneos
- Colores y grosores
- Borrar y deshacer

**Eventos:**
```javascript
socket.emit('draw-start', { x, y, color, width });
socket.emit('draw-move', { x, y });
socket.emit('draw-end');
```

---

### Desafío 3: Sistema de Votación en Tiempo Real

**Crear:** `examples/voting/`

**Características:**
- Crear encuestas
- Votar en tiempo real
- Gráficos actualizados en vivo
- Un voto por usuario
- Resultados en vivo

---

### Desafío 4: Monitor de Servidores

**Crear:** `examples/server-monitor/`

**Características:**
- Múltiples servidores
- Métricas: CPU, RAM, Disco, Red
- Alertas automáticas
- Historial de 24 horas
- Estado: Online/Warning/Offline

---

## Proyectos Finales

### Proyecto 1: Plataforma de Soporte

Combinar múltiples ejemplos:
- Chat para comunicación
- Dashboard para métricas del soporte
- Notificaciones para nuevos tickets
- Sistema de presencia de agentes

### Proyecto 2: Trading Dashboard

- Precios en tiempo real
- Gráficos de velas
- Órdenes de compra/venta
- Alertas de precio

### Proyecto 3: Classroom Virtual

- Videoconferencia (simulada con WebRTC)
- Chat de clase
- Pizarra compartida
- Levantar mano
- Encuestas en vivo

---

## Checklist de Conceptos

Marca cuando hayas entendido:

- [ ] Conexión y desconexión de WebSocket
- [ ] Emisión de eventos cliente ↔ servidor
- [ ] Broadcasting a múltiples clientes
- [ ] Rooms para agrupar conexiones
- [ ] Namespaces para separar lógica
- [ ] Acknowledgements (callbacks)
- [ ] Manejo de errores
- [ ] Autenticación básica
- [ ] Rate limiting
- [ ] Persistencia de datos
- [ ] Reconexión automática
- [ ] Sincronización de estado

---

## Recursos de Ayuda

### Debugging

```javascript
// Activar logs de Socket.io
localStorage.debug = 'socket.io-client:socket';

// En servidor
const io = socketIO(server, {
  transports: ['websocket', 'polling'],
  allowEIO3: true
});
```

### Testing

```javascript
// Simular múltiples clientes
for (let i = 0; i < 10; i++) {
  const socket = io('http://localhost:3001');
  socket.emit('join-room', {
    username: `User${i}`,
    room: 'test'
  });
}
```

---

## Próximos Pasos

1. Completa ejercicios básicos (1-3)
2. Revisa GUIA.md para conceptos
3. Avanza a ejercicios intermedios (4-6)
4. Experimenta con desafíos (7-10)
5. Crea tu propio proyecto

---

¡Feliz aprendizaje de WebSockets! 🚀
