import { useState, useEffect, useRef } from 'react'
import useWebSocket from '../hooks/useWebSocket'
import './ChatRoom.css'

function ChatRoom({ username, onLogout }) {
  const [message, setMessage] = useState('')
  const messagesEndRef = useRef(null)

  const { messages, sendMessage, isConnected, onlineUsers } = useWebSocket(username)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = (e) => {
    e.preventDefault()
    if (message.trim() && isConnected) {
      sendMessage(message)
      setMessage('')
    }
  }

  const formatTime = (timestamp) => {
    const date = new Date(timestamp)
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div className="chat-room">
      <div className="chat-header">
        <div className="connection-status">
          <span className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`}></span>
          <span>{isConnected ? 'Connected' : 'Disconnected'}</span>
        </div>
        <div className="online-users">
          <span>👥 {onlineUsers} online</span>
        </div>
        <button onClick={onLogout} className="logout-btn">Logout</button>
      </div>

      <div className="messages-container">
        {messages.map((msg, index) => (
          <div key={index} className={`message-wrapper ${msg.type}`}>
            {msg.type === 'message' && (
              <div className={`message ${msg.username === username ? 'own-message' : 'other-message'}`}>
                <div className="message-header">
                  <span className="message-username">{msg.username}</span>
                  <span className="message-time">{formatTime(msg.timestamp)}</span>
                </div>
                <div className="message-content">{msg.message}</div>
              </div>
            )}

            {msg.type === 'user_joined' && (
              <div className="system-message">
                <span>✅ {msg.username} joined the chat</span>
                <span className="message-time">{formatTime(msg.timestamp)}</span>
              </div>
            )}

            {msg.type === 'user_left' && (
              <div className="system-message">
                <span>❌ {msg.username} left the chat</span>
                <span className="message-time">{formatTime(msg.timestamp)}</span>
              </div>
            )}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="message-form">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder={isConnected ? "Type a message..." : "Connecting..."}
          disabled={!isConnected}
          maxLength={500}
        />
        <button type="submit" disabled={!message.trim() || !isConnected}>
          Send
        </button>
      </form>
    </div>
  )
}

export default ChatRoom
