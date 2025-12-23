/**
 * WebSocket Service para conectarse al backend FastAPI
 */

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';

class WebSocketService {
  constructor() {
    this.ws = null;
    this.listeners = new Map();
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectInterval = 3000;
  }

  /**
   * Conectar al servidor WebSocket
   */
  connect(username, room) {
    return new Promise((resolve, reject) => {
      try {
        const url = `${WS_URL}/ws/${encodeURIComponent(username)}/${encodeURIComponent(room)}`;
        console.log('Conectando a:', url);

        this.ws = new WebSocket(url);

        this.ws.onopen = () => {
          console.log('✅ Conectado al servidor WebSocket');
          this.reconnectAttempts = 0;
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
          } catch (error) {
            console.error('Error parseando mensaje:', error);
          }
        };

        this.ws.onerror = (error) => {
          console.error('❌ Error de WebSocket:', error);
          reject(error);
        };

        this.ws.onclose = (event) => {
          console.log('Conexión cerrada:', event.code, event.reason);
          this.handleReconnect(username, room);
        };

      } catch (error) {
        console.error('Error creando WebSocket:', error);
        reject(error);
      }
    });
  }

  /**
   * Manejar reconexión automática
   */
  handleReconnect(username, room) {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Reintentando conexión (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);

      setTimeout(() => {
        this.connect(username, room).catch(err => {
          console.error('Error en reconexión:', err);
        });
      }, this.reconnectInterval);
    } else {
      console.error('Máximo de reintentos alcanzado');
      this.emit('max_reconnect_attempts');
    }
  }

  /**
   * Desconectar del servidor
   */
  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.listeners.clear();
  }

  /**
   * Enviar mensaje
   */
  sendMessage(text) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      const message = {
        type: 'message',
        text: text
      };
      this.ws.send(JSON.stringify(message));
    } else {
      console.error('WebSocket no está conectado');
    }
  }

  /**
   * Enviar indicador de "escribiendo"
   */
  sendTyping(isTyping) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      const message = {
        type: 'typing',
        is_typing: isTyping
      };
      this.ws.send(JSON.stringify(message));
    }
  }

  /**
   * Manejar mensajes recibidos
   */
  handleMessage(data) {
    const { type } = data;

    // Emitir evento según el tipo de mensaje
    this.emit(type, data);

    // También emitir evento genérico
    this.emit('message', data);
  }

  /**
   * Registrar un listener para un tipo de evento
   */
  on(eventType, callback) {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, []);
    }
    this.listeners.get(eventType).push(callback);
  }

  /**
   * Eliminar un listener
   */
  off(eventType, callback) {
    if (this.listeners.has(eventType)) {
      const callbacks = this.listeners.get(eventType);
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }

  /**
   * Emitir un evento a todos los listeners
   */
  emit(eventType, data) {
    if (this.listeners.has(eventType)) {
      this.listeners.get(eventType).forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error('Error en callback:', error);
        }
      });
    }
  }

  /**
   * Verificar estado de conexión
   */
  isConnected() {
    return this.ws && this.ws.readyState === WebSocket.OPEN;
  }
}

// Exportar una instancia única (singleton)
export default new WebSocketService();
