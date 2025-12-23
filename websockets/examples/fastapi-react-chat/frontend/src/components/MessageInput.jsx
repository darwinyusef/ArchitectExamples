import { useState, useRef, useEffect } from 'react'
import './MessageInput.css'

function MessageInput({ onSendMessage, onTyping, disabled }) {
  const [message, setMessage] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const typingTimeoutRef = useRef(null)

  const handleChange = (e) => {
    const value = e.target.value
    setMessage(value)

    // Indicador de escritura
    if (value && !isTyping) {
      setIsTyping(true)
      onTyping(true)
    }

    // Reset timeout
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current)
    }

    typingTimeoutRef.current = setTimeout(() => {
      setIsTyping(false)
      onTyping(false)
    }, 1000)
  }

  const handleSubmit = (e) => {
    e.preventDefault()

    if (message.trim() && !disabled) {
      onSendMessage(message.trim())
      setMessage('')
      setIsTyping(false)
      onTyping(false)

      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current)
      }
    }
  }

  useEffect(() => {
    return () => {
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current)
      }
    }
  }, [])

  return (
    <form className="message-input" onSubmit={handleSubmit}>
      <input
        type="text"
        value={message}
        onChange={handleChange}
        placeholder={disabled ? 'Conectando...' : 'Escribe un mensaje...'}
        disabled={disabled}
        autoComplete="off"
      />
      <button
        type="submit"
        disabled={!message.trim() || disabled}
        className="send-btn"
      >
        Enviar
      </button>
    </form>
  )
}

export default MessageInput
