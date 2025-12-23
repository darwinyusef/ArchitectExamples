import { useState, useEffect, useRef } from 'react'
import websocketService from '../services/websocketService'
import MessageList from './MessageList'
import UsersList from './UsersList'
import MessageInput from './MessageInput'
import './ChatScreen.css'

function ChatScreen({ username, room, onLogout }) {
  const [messages, setMessages] = useState([])
  const [users, setUsers] = useState([])
  const [typingUsers, setTypingUsers] = useState(new Set())
  const [isConnected, setIsConnected] = useState(false)
  const [connectionError, setConnectionError] = useState(null)

  useEffect(() => {
    // Conectar al WebSocket
    connectToChat()

    return () => {
      // Limpiar al desmontar
      websocketService.disconnect()
    }
  }, [username, room])

  const connectToChat = async () => {
    try {
      await websocketService.connect(username, room)
      setIsConnected(true)
      setConnectionError(null)

      // Configurar listeners
      setupListeners()
    } catch (error) {
      console.error('Error conectando:', error)
      setConnectionError('No se pudo conectar al servidor')
      setIsConnected(false)
    }
  }

  const setupListeners = () => {
    // Historial de mensajes
    websocketService.on('history', (data) => {
      setMessages(data.messages || [])
    })

    // Nuevo mensaje
    websocketService.on('message', (data) => {
      setMessages(prev => [...prev, data])
    })

    // Usuario se unió
    websocketService.on('user_joined', (data) => {
      const systemMessage = {
        type: 'system',
        text: `${data.username} se unió al chat`,
        timestamp: data.timestamp
      }
      setMessages(prev => [...prev, systemMessage])
    })

    // Usuario salió
    websocketService.on('user_left', (data) => {
      const systemMessage = {
        type: 'system',
        text: `${data.username} salió del chat`,
        timestamp: data.timestamp
      }
      setMessages(prev => [...prev, systemMessage])
    })

    // Lista de usuarios actualizada
    websocketService.on('user_list', (data) => {
      setUsers(data.users || [])
    })

    // Usuario escribiendo
    websocketService.on('typing', (data) => {
      if (data.is_typing) {
        setTypingUsers(prev => new Set([...prev, data.username]))
      } else {
        setTypingUsers(prev => {
          const newSet = new Set(prev)
          newSet.delete(data.username)
          return newSet
        })
      }
    })

    // Máximo de reintentos alcanzado
    websocketService.on('max_reconnect_attempts', () => {
      setConnectionError('Conexión perdida. Por favor recarga la página.')
      setIsConnected(false)
    })
  }

  const handleSendMessage = (text) => {
    websocketService.sendMessage(text)
  }

  const handleTyping = (isTyping) => {
    websocketService.sendTyping(isTyping)
  }

  const handleLogout = () => {
    websocketService.disconnect()
    onLogout()
  }

  return (
    <div className="chat-screen">
      {/* Header */}
      <div className="chat-header">
        <div className="chat-info">
          <div className="room-name">
            <span className="status-dot" style={{
              backgroundColor: isConnected ? '#4caf50' : '#f44336'
            }}></span>
            Sala: {room}
          </div>
          <div className="user-name">@{username}</div>
        </div>
        <button onClick={handleLogout} className="logout-btn">
          Salir
        </button>
      </div>

      {/* Contenedor principal */}
      <div className="chat-container">
        {/* Sidebar de usuarios */}
        <UsersList users={users} currentUsername={username} />

        {/* Área de chat */}
        <div className="chat-main">
          {/* Error de conexión */}
          {connectionError && (
            <div className="connection-error">
              ⚠️ {connectionError}
            </div>
          )}

          {/* Lista de mensajes */}
          <MessageList
            messages={messages}
            currentUsername={username}
            typingUsers={typingUsers}
          />

          {/* Input de mensaje */}
          <MessageInput
            onSendMessage={handleSendMessage}
            onTyping={handleTyping}
            disabled={!isConnected}
          />
        </div>
      </div>
    </div>
  )
}

export default ChatScreen
