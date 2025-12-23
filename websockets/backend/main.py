from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
import json
from datetime import datetime

app = FastAPI(title="WebSocket Chat API")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Manager para manejar las conexiones WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.users: Dict[WebSocket, str] = {}

    async def connect(self, websocket: WebSocket, username: str):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.users[websocket] = username

        # Notificar a todos que un nuevo usuario se conectó
        await self.broadcast({
            "type": "user_joined",
            "username": username,
            "timestamp": datetime.now().isoformat(),
            "online_users": len(self.active_connections)
        })

    def disconnect(self, websocket: WebSocket):
        username = self.users.get(websocket, "Unknown")
        self.active_connections.remove(websocket)
        if websocket in self.users:
            del self.users[websocket]
        return username

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

@app.get("/")
async def root():
    return {
        "message": "WebSocket Server is running",
        "active_connections": len(manager.active_connections),
        "endpoints": {
            "websocket": "/ws/{username}",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "active_connections": len(manager.active_connections),
        "users": list(manager.users.values())
    }

@app.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    await manager.connect(websocket, username)

    try:
        while True:
            # Recibir mensaje del cliente
            data = await websocket.receive_text()
            message_data = json.loads(data)

            # Preparar el mensaje para broadcast
            broadcast_message = {
                "type": "message",
                "username": username,
                "message": message_data.get("message", ""),
                "timestamp": datetime.now().isoformat()
            }

            # Enviar a todos los clientes conectados
            await manager.broadcast(broadcast_message)

    except WebSocketDisconnect:
        username = manager.disconnect(websocket)
        await manager.broadcast({
            "type": "user_left",
            "username": username,
            "timestamp": datetime.now().isoformat(),
            "online_users": len(manager.active_connections)
        })
    except Exception as e:
        print(f"Error: {e}")
        username = manager.disconnect(websocket)
        await manager.broadcast({
            "type": "user_left",
            "username": username,
            "timestamp": datetime.now().isoformat(),
            "online_users": len(manager.active_connections)
        })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
