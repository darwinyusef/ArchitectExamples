/**
 * Cliente de Chat - WebSocket
 */

const socket = io();

// Elementos del DOM
const loginScreen = document.getElementById('login-screen');
const chatScreen = document.getElementById('chat-screen');
const loginForm = document.getElementById('login-form');
const messageForm = document.getElementById('message-form');
const messageInput = document.getElementById('message-input');
const messagesContainer = document.getElementById('messages');
const usernameInput = document.getElementById('username');
const roomInput = document.getElementById('room');
const roomNameDisplay = document.getElementById('room-name');
const usersCountDisplay = document.getElementById('users-count');
const usersListContainer = document.getElementById('users-list');
const leaveBtn = document.getElementById('leave-btn');
const typingIndicator = document.getElementById('typing-indicator');

// Estado local
let currentUsername = '';
let currentRoom = '';
let typingTimeout = null;

// Unirse al chat
loginForm.addEventListener('submit', (e) => {
  e.preventDefault();

  currentUsername = usernameInput.value.trim();
  currentRoom = roomInput.value.trim();

  if (currentUsername && currentRoom) {
    // Enviar evento de unión
    socket.emit('join-room', {
      username: currentUsername,
      room: currentRoom
    });

    // Cambiar a pantalla de chat
    loginScreen.classList.add('hidden');
    chatScreen.style.display = 'flex';

    // Actualizar UI
    roomNameDisplay.textContent = `Sala: ${currentRoom}`;
  }
});

// Enviar mensaje
messageForm.addEventListener('submit', (e) => {
  e.preventDefault();

  const text = messageInput.value.trim();

  if (text) {
    // Enviar mensaje al servidor
    socket.emit('send-message', { text });

    // Limpiar input
    messageInput.value = '';

    // Detener indicador de escritura
    socket.emit('typing-stop');
  }
});

// Detectar escritura
let isTyping = false;
messageInput.addEventListener('input', () => {
  if (!isTyping) {
    isTyping = true;
    socket.emit('typing-start');
  }

  // Resetear timeout
  clearTimeout(typingTimeout);

  typingTimeout = setTimeout(() => {
    isTyping = false;
    socket.emit('typing-stop');
  }, 1000);
});

// Salir del chat
leaveBtn.addEventListener('click', () => {
  socket.disconnect();
  location.reload();
});

// Recibir historial de mensajes
socket.on('message-history', (messages) => {
  messagesContainer.innerHTML = '';
  messages.forEach(msg => {
    displayMessage(msg);
  });
  scrollToBottom();
});

// Nuevo mensaje
socket.on('new-message', (message) => {
  displayMessage(message);
  scrollToBottom();
});

// Mensaje privado
socket.on('private-message', (message) => {
  displayPrivateMessage(message);
  scrollToBottom();
});

// Usuario se unió
socket.on('user-joined', (data) => {
  displaySystemMessage(`${data.username} se unió al chat`);
  updateUsersCount(data.usersCount);
  scrollToBottom();
});

// Usuario salió
socket.on('user-left', (data) => {
  displaySystemMessage(`${data.username} salió del chat`);
  updateUsersCount(data.usersCount);
  scrollToBottom();
});

// Lista de usuarios
socket.on('user-list', (users) => {
  usersListContainer.innerHTML = '';

  users.forEach(user => {
    const userItem = document.createElement('div');
    userItem.className = 'user-item';
    userItem.textContent = user.username;

    // Resaltar usuario actual
    if (user.username === currentUsername) {
      userItem.style.fontWeight = 'bold';
      userItem.style.background = '#e3f2fd';
    }

    usersListContainer.appendChild(userItem);
  });
});

// Usuario escribiendo
const typingUsers = new Set();
socket.on('user-typing', (data) => {
  if (data.isTyping) {
    typingUsers.add(data.username);
  } else {
    typingUsers.delete(data.username);
  }

  updateTypingIndicator();
});

// Error
socket.on('error', (error) => {
  alert(error.message);
  console.error('Error:', error);
});

// Funciones auxiliares

function displayMessage(message) {
  const messageDiv = document.createElement('div');
  messageDiv.className = 'message';

  // Marcar mensajes propios
  if (message.username === currentUsername) {
    messageDiv.classList.add('own');
  }

  messageDiv.innerHTML = `
    <div class="message-header">
      <span class="message-author">${message.username}</span>
      <span class="message-time">${formatTime(message.timestamp)}</span>
    </div>
    <div class="message-text">${escapeHtml(message.text)}</div>
  `;

  messagesContainer.appendChild(messageDiv);
}

function displayPrivateMessage(message) {
  const messageDiv = document.createElement('div');
  messageDiv.className = 'message private-message';

  const isOwn = message.from === currentUsername;
  const displayName = isOwn ? `Tú → ${message.to}` : `${message.from} (privado)`;

  messageDiv.innerHTML = `
    <div class="message-header">
      <span class="message-author">${displayName}</span>
      <span class="message-time">${formatTime(message.timestamp)}</span>
    </div>
    <div class="message-text">🔒 ${escapeHtml(message.text)}</div>
  `;

  messagesContainer.appendChild(messageDiv);
}

function displaySystemMessage(text) {
  const messageDiv = document.createElement('div');
  messageDiv.className = 'system-message';
  messageDiv.textContent = text;
  messagesContainer.appendChild(messageDiv);
}

function updateUsersCount(count) {
  usersCountDisplay.textContent = `${count} usuario${count !== 1 ? 's' : ''} conectado${count !== 1 ? 's' : ''}`;
}

function updateTypingIndicator() {
  if (typingUsers.size > 0) {
    const users = Array.from(typingUsers);
    const text = users.length === 1
      ? `${users[0]} está escribiendo...`
      : `${users.join(', ')} están escribiendo...`;

    typingIndicator.textContent = text;
    typingIndicator.classList.remove('hidden');
  } else {
    typingIndicator.classList.add('hidden');
  }
}

function scrollToBottom() {
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function formatTime(timestamp) {
  const date = new Date(timestamp);
  return date.toLocaleTimeString('es-ES', {
    hour: '2-digit',
    minute: '2-digit'
  });
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// Auto-focus en el input de mensaje cuando se carga el chat
messageInput.addEventListener('focus', () => {
  messageInput.focus();
});
