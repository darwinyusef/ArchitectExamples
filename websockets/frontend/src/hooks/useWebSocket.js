import { useState, useEffect, useRef, useCallback } from 'react'

const WEBSOCKET_URL = 'ws://localhost:8000/ws'

function useWebSocket(username) {
  const [messages, setMessages] = useState([])
  const [isConnected, setIsConnected] = useState(false)
  const [onlineUsers, setOnlineUsers] = useState(0)
  const ws = useRef(null)
  const reconnectTimeout = useRef(null)

  const connect = useCallback(() => {
    if (!username) return

    try {
      // Crear conexión WebSocket
      ws.current = new WebSocket(`${WEBSOCKET_URL}/${username}`)

      ws.current.onopen = () => {
        console.log('WebSocket Connected')
        setIsConnected(true)
      }

      ws.current.onmessage = (event) => {
        const data = JSON.parse(event.data)
        console.log('Message received:', data)

        setMessages((prev) => [...prev, data])

        if (data.online_users !== undefined) {
          setOnlineUsers(data.online_users)
        }
      }

      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error)
      }

      ws.current.onclose = () => {
        console.log('WebSocket Disconnected')
        setIsConnected(false)

        // Intentar reconectar después de 3 segundos
        reconnectTimeout.current = setTimeout(() => {
          console.log('Attempting to reconnect...')
          connect()
        }, 3000)
      }
    } catch (error) {
      console.error('Error creating WebSocket:', error)
    }
  }, [username])

  useEffect(() => {
    connect()

    return () => {
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current)
      }
      if (ws.current) {
        ws.current.close()
      }
    }
  }, [connect])

  const sendMessage = useCallback((message) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({ message }))
    }
  }, [])

  return {
    messages,
    sendMessage,
    isConnected,
    onlineUsers
  }
}

export default useWebSocket
