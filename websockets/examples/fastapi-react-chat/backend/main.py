"""
FastAPI WebSocket Chat Backend
Sistema de chat en tiempo real con FastAPI y WebSockets
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
import json
import uuid

app = FastAPI(title="Chat WebSocket API", version="1.0.0")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic
class User(BaseModel):
    id: str
    username: str
    room: str

class Message(BaseModel):
    id: str
    username: str
    text: str
    room: str
    timestamp: str
    type: str = "message"

class ChatRoom(BaseModel):
    name: str
    users: List[str]
    message_count: int

# Almacenamiento en memoria
class ConnectionManager:
    def __init__(self):
        # websocket_id -> {websocket, username, room}
        self.active_connections: Dict[str, Dict] = {}
        # room_name -> [websocket_ids]
        self.rooms: Dict[str, List[str]] = {}
        # room_name -> [messages]
        self.message_history: Dict[str, List[Dict]] = {}

    async def connect(self, websocket: WebSocket, username: str, room: str):
        """Conectar un nuevo cliente"""
        await websocket.accept()

        # Generar ID único para la conexión
        connection_id = str(uuid.uuid4())

        # Guardar conexión
        self.active_connections[connection_id] = {
            "websocket": websocket,
            "username": username,
            "room": room,
            "id": connection_id
        }

        # Agregar a la sala
        if room not in self.rooms:
            self.rooms[room] = []
            self.message_history[room] = []

        self.rooms[room].append(connection_id)

        return connection_id

    def disconnect(self, connection_id: str):
        """Desconectar un cliente"""
        if connection_id in self.active_connections:
            connection = self.active_connections[connection_id]
            room = connection["room"]

            # Remover de la sala
            if room in self.rooms and connection_id in self.rooms[room]:
                self.rooms[room].remove(connection_id)

                # Limpiar sala vacía
                if len(self.rooms[room]) == 0:
                    del self.rooms[room]
                    # Opcional: limpiar historial
                    # del self.message_history[room]

            # Remover conexión
            del self.active_connections[connection_id]

    async def send_personal_message(self, message: dict, connection_id: str):
        """Enviar mensaje a un cliente específico"""
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]["websocket"]
            await websocket.send_json(message)

    async def broadcast_to_room(self, message: dict, room: str, exclude_id: Optional[str] = None):
        """Enviar mensaje a todos en una sala"""
        if room in self.rooms:
            for connection_id in self.rooms[room]:
                if exclude_id and connection_id == exclude_id:
                    continue
                await self.send_personal_message(message, connection_id)

    async def broadcast_to_all(self, message: dict, exclude_id: Optional[str] = None):
        """Enviar mensaje a todos los clientes"""
        for connection_id in self.active_connections.keys():
            if exclude_id and connection_id == exclude_id:
                continue
            await self.send_personal_message(message, connection_id)

    def get_room_users(self, room: str) -> List[Dict[str, str]]:
        """Obtener lista de usuarios en una sala"""
        if room not in self.rooms:
            return []

        users = []
        for connection_id in self.rooms[room]:
            if connection_id in self.active_connections:
                conn = self.active_connections[connection_id]
                users.append({
                    "id": connection_id,
                    "username": conn["username"]
                })
        return users

    def save_message(self, room: str, message: Dict):
        """Guardar mensaje en el historial"""
        if room not in self.message_history:
            self.message_history[room] = []

        self.message_history[room].append(message)

        # Limitar historial a 100 mensajes
        if len(self.message_history[room]) > 100:
            self.message_history[room] = self.message_history[room][-100:]

    def get_message_history(self, room: str) -> List[Dict]:
        """Obtener historial de mensajes de una sala"""
        return self.message_history.get(room, [])

manager = ConnectionManager()

# Endpoints REST
@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "FastAPI WebSocket Chat API",
        "version": "1.0.0",
        "websocket_url": "ws://localhost:8000/ws/{username}/{room}"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "active_connections": len(manager.active_connections),
        "active_rooms": len(manager.rooms)
    }

@app.get("/rooms", response_model=List[ChatRoom])
async def get_rooms():
    """Obtener lista de salas activas"""
    rooms_list = []
    for room_name, connection_ids in manager.rooms.items():
        users = [manager.active_connections[cid]["username"]
                for cid in connection_ids
                if cid in manager.active_connections]

        rooms_list.append({
            "name": room_name,
            "users": users,
            "message_count": len(manager.message_history.get(room_name, []))
        })

    return rooms_list

@app.get("/rooms/{room_name}/history")
async def get_room_history(room_name: str, limit: int = 50):
    """Obtener historial de mensajes de una sala"""
    history = manager.get_message_history(room_name)
    return {
        "room": room_name,
        "messages": history[-limit:] if history else []
    }

@app.get("/stats")
async def get_stats():
    """Obtener estadísticas del servidor"""
    total_messages = sum(len(messages) for messages in manager.message_history.values())

    return {
        "active_connections": len(manager.active_connections),
        "active_rooms": len(manager.rooms),
        "total_messages": total_messages,
        "rooms": list(manager.rooms.keys())
    }

# WebSocket endpoint
@app.websocket("/ws/{username}/{room}")
async def websocket_endpoint(websocket: WebSocket, username: str, room: str):
    """
    WebSocket endpoint principal
    URL: ws://localhost:8000/ws/{username}/{room}
    """

    # Conectar cliente
    connection_id = await manager.connect(websocket, username, room)

    print(f"✅ {username} conectado a la sala '{room}' (ID: {connection_id})")

    try:
        # Enviar historial de mensajes al nuevo usuario
        history = manager.get_message_history(room)
        await manager.send_personal_message({
            "type": "history",
            "messages": history
        }, connection_id)

        # Notificar a la sala que un usuario se unió
        join_message = {
            "type": "user_joined",
            "username": username,
            "timestamp": datetime.now().isoformat(),
            "users_count": len(manager.rooms[room])
        }
        await manager.broadcast_to_room(join_message, room)

        # Enviar lista de usuarios actualizada
        users_list = manager.get_room_users(room)
        await manager.broadcast_to_room({
            "type": "user_list",
            "users": users_list
        }, room)

        # Loop principal: recibir y procesar mensajes
        while True:
            # Recibir mensaje del cliente
            data = await websocket.receive_text()
            message_data = json.loads(data)

            message_type = message_data.get("type", "message")

            if message_type == "message":
                # Mensaje de chat normal
                message = {
                    "id": str(uuid.uuid4()),
                    "type": "message",
                    "username": username,
                    "text": message_data.get("text", ""),
                    "room": room,
                    "timestamp": datetime.now().isoformat()
                }

                # Guardar en historial
                manager.save_message(room, message)

                # Broadcast a todos en la sala
                await manager.broadcast_to_room(message, room)

                print(f"💬 [{room}] {username}: {message['text']}")

            elif message_type == "typing":
                # Usuario escribiendo
                typing_message = {
                    "type": "typing",
                    "username": username,
                    "is_typing": message_data.get("is_typing", False)
                }
                await manager.broadcast_to_room(typing_message, room, exclude_id=connection_id)

            elif message_type == "ping":
                # Ping/pong para mantener conexión viva
                await manager.send_personal_message({"type": "pong"}, connection_id)

    except WebSocketDisconnect:
        print(f"❌ {username} desconectado de '{room}'")
    except Exception as e:
        print(f"⚠️  Error en conexión de {username}: {e}")
    finally:
        # Limpiar conexión
        manager.disconnect(connection_id)

        # Notificar a la sala que el usuario salió
        if room in manager.rooms:
            leave_message = {
                "type": "user_left",
                "username": username,
                "timestamp": datetime.now().isoformat(),
                "users_count": len(manager.rooms.get(room, []))
            }
            await manager.broadcast_to_room(leave_message, room)

            # Actualizar lista de usuarios
            users_list = manager.get_room_users(room)
            await manager.broadcast_to_room({
                "type": "user_list",
                "users": users_list
            }, room)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
