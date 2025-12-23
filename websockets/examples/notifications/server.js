/**
 * EJEMPLO 3: SISTEMA DE NOTIFICACIONES PUSH
 * Sistema de notificaciones en tiempo real para múltiples usuarios
 */

const express = require('express');
const http = require('http');
const socketIO = require('socket.io');
const path = require('path');
const { v4: uuidv4 } = require('uuid');

const app = express();
const server = http.createServer(app);
const io = socketIO(server);

const PORT = process.env.PORT || 3003;

app.use(express.static(path.join(__dirname, 'public')));
app.use(express.json());

const users = new Map(); // userId -> {socketId, username, preferences}
const notifications = new Map(); // userId -> Array of notifications

// API para enviar notificación (simulado)
app.post('/api/notify', (req, res) => {
  const { userId, title, message, type = 'info' } = req.body;

  if (!userId || !message) {
    return res.status(400).json({ error: 'userId y message son requeridos' });
  }

  const notification = {
    id: uuidv4(),
    title: title || 'Notificación',
    message,
    type,
    timestamp: new Date().toISOString(),
    read: false
  };

  // Guardar notificación
  if (!notifications.has(userId)) {
    notifications.set(userId, []);
  }
  notifications.get(userId).unshift(notification);

  // Enviar a usuario si está conectado
  const user = Array.from(users.values()).find(u => u.userId === userId);
  if (user) {
    io.to(user.socketId).emit('notification', notification);
  }

  res.json({ success: true, notification });
});

io.on('connection', (socket) => {
  console.log('Cliente conectado:', socket.id);

  socket.on('register', ({ userId, username }) => {
    users.set(socket.id, { socketId: socket.id, userId, username });

    // Enviar notificaciones pendientes
    const userNotifications = notifications.get(userId) || [];
    socket.emit('notifications-history', userNotifications);

    console.log(`Usuario registrado: ${username} (${userId})`);
  });

  socket.on('mark-read', ({ notificationId, userId }) => {
    const userNotifications = notifications.get(userId);
    if (userNotifications) {
      const notif = userNotifications.find(n => n.id === notificationId);
      if (notif) notif.read = true;
    }
  });

  socket.on('disconnect', () => {
    users.delete(socket.id);
    console.log('Cliente desconectado:', socket.id);
  });
});

// Simular notificaciones automáticas cada 10 segundos
setInterval(() => {
  users.forEach((user) => {
    if (Math.random() > 0.7) {
      const types = ['info', 'success', 'warning', 'error'];
      const messages = [
        'Tienes un nuevo mensaje',
        'Tu pedido ha sido enviado',
        'Actualización disponible',
        'Nuevo seguidor en tu perfil'
      ];

      const notification = {
        id: uuidv4(),
        title: 'Notificación Automática',
        message: messages[Math.floor(Math.random() * messages.length)],
        type: types[Math.floor(Math.random() * types.length)],
        timestamp: new Date().toISOString(),
        read: false
      };

      if (!notifications.has(user.userId)) {
        notifications.set(user.userId, []);
      }
      notifications.get(user.userId).unshift(notification);

      io.to(user.socketId).emit('notification', notification);
    }
  });
}, 10000);

server.listen(PORT, () => {
  console.log(`\n🔔 Sistema de notificaciones en http://localhost:${PORT}`);
  console.log(`API: POST http://localhost:${PORT}/api/notify\n`);
});
