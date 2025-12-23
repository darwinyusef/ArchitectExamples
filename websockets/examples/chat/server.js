/**
 * EJEMPLO 1: CHAT EN TIEMPO REAL
 *
 * Este ejemplo implementa un sistema de chat completo con:
 * - Salas (rooms) múltiples
 * - Usuarios con nombres
 * - Mensajes privados
 * - Indicador de "escribiendo..."
 * - Lista de usuarios conectados
 * - Historial de mensajes
 */

const express = require('express');
const http = require('http');
const socketIO = require('socket.io');
const path = require('path');

const app = express();
const server = http.createServer(app);
const io = socketIO(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});

const PORT = process.env.PORT || 3001;

// Servir archivos estáticos
app.use(express.static(path.join(__dirname, 'public')));

// Almacenamiento en memoria
const users = new Map(); // socketId -> { username, room }
const rooms = new Map(); // roomName -> Set of socketIds
const messageHistory = new Map(); // roomName -> Array of messages

// Eventos de Socket.io
io.on('connection', (socket) => {
  console.log(`✅ Cliente conectado: ${socket.id}`);

  // Unirse a una sala de chat
  socket.on('join-room', ({ username, room }) => {
    // Validación
    if (!username || !room) {
      socket.emit('error', { message: 'Username y room son requeridos' });
      return;
    }

    // Guardar información del usuario
    users.set(socket.id, { username, room });

    // Agregar a la sala
    socket.join(room);

    // Inicializar sala si no existe
    if (!rooms.has(room)) {
      rooms.set(room, new Set());
      messageHistory.set(room, []);
    }
    rooms.get(room).add(socket.id);

    console.log(`👤 ${username} se unió a la sala: ${room}`);

    // Enviar historial de mensajes al nuevo usuario
    const history = messageHistory.get(room);
    socket.emit('message-history', history);

    // Notificar a todos en la sala
    io.to(room).emit('user-joined', {
      username,
      timestamp: new Date().toISOString(),
      usersCount: rooms.get(room).size
    });

    // Enviar lista actualizada de usuarios
    updateUserList(room);
  });

  // Enviar mensaje
  socket.on('send-message', (messageData) => {
    const user = users.get(socket.id);
    if (!user) {
      socket.emit('error', { message: 'Debes unirte a una sala primero' });
      return;
    }

    const message = {
      id: `${socket.id}-${Date.now()}`,
      username: user.username,
      text: messageData.text,
      room: user.room,
      timestamp: new Date().toISOString(),
      type: 'message'
    };

    // Guardar en historial
    const history = messageHistory.get(user.room);
    history.push(message);

    // Limitar historial a 100 mensajes
    if (history.length > 100) {
      history.shift();
    }

    // Enviar a todos en la sala
    io.to(user.room).emit('new-message', message);

    console.log(`💬 ${user.username} en ${user.room}: ${messageData.text}`);
  });

  // Mensaje privado
  socket.on('private-message', ({ toUsername, text }) => {
    const sender = users.get(socket.id);
    if (!sender) return;

    // Encontrar el socket del destinatario
    let recipientSocketId = null;
    for (const [socketId, userData] of users.entries()) {
      if (userData.username === toUsername && userData.room === sender.room) {
        recipientSocketId = socketId;
        break;
      }
    }

    if (!recipientSocketId) {
      socket.emit('error', { message: `Usuario ${toUsername} no encontrado` });
      return;
    }

    const privateMsg = {
      from: sender.username,
      to: toUsername,
      text,
      timestamp: new Date().toISOString(),
      type: 'private'
    };

    // Enviar al destinatario y al remitente
    io.to(recipientSocketId).emit('private-message', privateMsg);
    socket.emit('private-message', privateMsg);

    console.log(`🔒 ${sender.username} → ${toUsername}: ${text}`);
  });

  // Usuario escribiendo
  socket.on('typing-start', () => {
    const user = users.get(socket.id);
    if (!user) return;

    socket.to(user.room).emit('user-typing', {
      username: user.username,
      isTyping: true
    });
  });

  socket.on('typing-stop', () => {
    const user = users.get(socket.id);
    if (!user) return;

    socket.to(user.room).emit('user-typing', {
      username: user.username,
      isTyping: false
    });
  });

  // Desconexión
  socket.on('disconnect', () => {
    const user = users.get(socket.id);

    if (user) {
      const { username, room } = user;

      // Remover de la sala
      if (rooms.has(room)) {
        rooms.get(room).delete(socket.id);

        // Limpiar sala vacía
        if (rooms.get(room).size === 0) {
          rooms.delete(room);
          messageHistory.delete(room);
        } else {
          // Notificar a los demás
          io.to(room).emit('user-left', {
            username,
            timestamp: new Date().toISOString(),
            usersCount: rooms.get(room).size
          });

          updateUserList(room);
        }
      }

      users.delete(socket.id);
      console.log(`❌ ${username} desconectado de ${room}`);
    } else {
      console.log(`❌ Cliente desconectado: ${socket.id}`);
    }
  });
});

// Función auxiliar para actualizar lista de usuarios
function updateUserList(room) {
  const roomUsers = [];

  for (const socketId of rooms.get(room)) {
    const user = users.get(socketId);
    if (user) {
      roomUsers.push({
        username: user.username,
        socketId: socketId
      });
    }
  }

  io.to(room).emit('user-list', roomUsers);
}

// Iniciar servidor
server.listen(PORT, () => {
  console.log(`\n🚀 Servidor de Chat ejecutándose en http://localhost:${PORT}`);
  console.log(`📋 Salas activas: ${rooms.size}`);
  console.log(`👥 Usuarios conectados: ${users.size}\n`);
});

// Estadísticas cada 30 segundos
setInterval(() => {
  console.log(`📊 Estadísticas:
    - Salas activas: ${rooms.size}
    - Usuarios conectados: ${users.size}
    - Mensajes en historial: ${Array.from(messageHistory.values()).reduce((acc, hist) => acc + hist.length, 0)}
  `);
}, 30000);
