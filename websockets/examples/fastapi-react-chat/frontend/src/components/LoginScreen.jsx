import { useState } from 'react'
import './LoginScreen.css'

function LoginScreen({ onLogin }) {
  const [username, setUsername] = useState('')
  const [room, setRoom] = useState('general')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (username.trim() && room.trim()) {
      onLogin(username.trim(), room.trim())
    }
  }

  return (
    <div className="login-screen">
      <div className="login-card">
        <h1>💬 FastAPI + React Chat</h1>
        <p className="subtitle">Chat en tiempo real con WebSockets</p>

        <form onSubmit={handleSubmit}>
          <div className="input-group">
            <label htmlFor="username">Nombre de usuario</label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Tu nombre..."
              required
              autoFocus
            />
          </div>

          <div className="input-group">
            <label htmlFor="room">Sala de chat</label>
            <input
              type="text"
              id="room"
              value={room}
              onChange={(e) => setRoom(e.target.value)}
              placeholder="general"
              required
            />
          </div>

          <button type="submit" className="login-btn">
            Unirse al Chat
          </button>
        </form>

        <div className="tech-stack">
          <span className="badge">FastAPI</span>
          <span className="badge">React</span>
          <span className="badge">WebSocket</span>
          <span className="badge">Docker</span>
        </div>
      </div>
    </div>
  )
}

export default LoginScreen
