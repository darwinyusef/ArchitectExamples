import { useState } from 'react'
import LoginScreen from './components/LoginScreen'
import ChatScreen from './components/ChatScreen'
import './App.css'

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [username, setUsername] = useState('')
  const [room, setRoom] = useState('')

  const handleLogin = (user, chatRoom) => {
    setUsername(user)
    setRoom(chatRoom)
    setIsLoggedIn(true)
  }

  const handleLogout = () => {
    setIsLoggedIn(false)
    setUsername('')
    setRoom('')
  }

  return (
    <div className="app">
      {!isLoggedIn ? (
        <LoginScreen onLogin={handleLogin} />
      ) : (
        <ChatScreen
          username={username}
          room={room}
          onLogout={handleLogout}
        />
      )}
    </div>
  )
}

export default App
