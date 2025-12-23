import { useState } from 'react'
import ChatRoom from './components/ChatRoom'
import Login from './components/Login'
import './App.css'

function App() {
  const [username, setUsername] = useState('')
  const [isLoggedIn, setIsLoggedIn] = useState(false)

  const handleLogin = (name) => {
    setUsername(name)
    setIsLoggedIn(true)
  }

  const handleLogout = () => {
    setUsername('')
    setIsLoggedIn(false)
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>WebSocket Chat App</h1>
        {isLoggedIn && <p className="user-info">Logged in as: <strong>{username}</strong></p>}
      </header>

      {!isLoggedIn ? (
        <Login onLogin={handleLogin} />
      ) : (
        <ChatRoom username={username} onLogout={handleLogout} />
      )}
    </div>
  )
}

export default App
