import { useEffect, useRef } from 'react'
import './MessageList.css'

function MessageList({ messages, currentUsername, typingUsers }) {
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, typingUsers])

  const formatTime = (timestamp) => {
    const date = new Date(timestamp)
    return date.toLocaleTimeString('es-ES', {
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div className="message-list">
      {messages.map((msg, index) => {
        if (msg.type === 'system') {
          return (
            <div key={index} className="system-message">
              {msg.text}
            </div>
          )
        }

        const isOwn = msg.username === currentUsername

        return (
          <div
            key={msg.id || index}
            className={`message ${isOwn ? 'own' : ''}`}
          >
            <div className="message-header">
              <span className="message-author">{msg.username}</span>
              <span className="message-time">{formatTime(msg.timestamp)}</span>
            </div>
            <div className="message-bubble">
              {msg.text}
            </div>
          </div>
        )
      })}

      {/* Indicador de escribiendo */}
      {typingUsers.size > 0 && (
        <div className="typing-indicator">
          {Array.from(typingUsers).join(', ')} {typingUsers.size === 1 ? 'está' : 'están'} escribiendo
          <span className="typing-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
      )}

      <div ref={messagesEndRef} />
    </div>
  )
}

export default MessageList
