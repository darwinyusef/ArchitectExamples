from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Set
import asyncio
import json
from datetime import datetime


class ConnectionManager:
    """
    Gestor de conexiones WebSocket con soporte para múltiples rooms
    Demuestra manejo de concurrencia con múltiples clientes
    """

    def __init__(self):
        # Diccionario de rooms: room_id -> {peer_id -> websocket}
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}
        # Lock para operaciones thread-safe
        self.lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, room_id: str, peer_id: str):
        """Conecta un nuevo peer a un room"""
        await websocket.accept()

        async with self.lock:
            if room_id not in self.active_connections:
                self.active_connections[room_id] = {}

            self.active_connections[room_id][peer_id] = websocket

        # Notificar a otros peers en el room
        await self.broadcast_to_room(
            room_id,
            {
                "type": "peer_joined",
                "peer_id": peer_id,
                "timestamp": datetime.utcnow().isoformat(),
                "total_peers": len(self.active_connections[room_id])
            },
            exclude_peer=peer_id
        )

    async def disconnect(self, room_id: str, peer_id: str):
        """Desconecta un peer de un room"""
        async with self.lock:
            if room_id in self.active_connections:
                if peer_id in self.active_connections[room_id]:
                    del self.active_connections[room_id][peer_id]

                # Limpiar room vacío
                if not self.active_connections[room_id]:
                    del self.active_connections[room_id]

        # Notificar a otros peers
        if room_id in self.active_connections:
            await self.broadcast_to_room(
                room_id,
                {
                    "type": "peer_left",
                    "peer_id": peer_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "total_peers": len(self.active_connections.get(room_id, {}))
                }
            )

    async def send_personal_message(
        self,
        message: dict,
        room_id: str,
        target_peer_id: str
    ):
        """Envía un mensaje a un peer específico"""
        if room_id in self.active_connections:
            if target_peer_id in self.active_connections[room_id]:
                websocket = self.active_connections[room_id][target_peer_id]
                await websocket.send_json(message)

    async def broadcast_to_room(
        self,
        room_id: str,
        message: dict,
        exclude_peer: str = None
    ):
        """
        Broadcast a todos los peers en un room (excepto el excluido)
        Usa asyncio.gather para envíos concurrentes
        """
        if room_id not in self.active_connections:
            return

        tasks = []
        for peer_id, websocket in self.active_connections[room_id].items():
            if peer_id != exclude_peer:
                tasks.append(websocket.send_json(message))

        # Enviar todos los mensajes en paralelo
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def forward_signal(
        self,
        room_id: str,
        from_peer_id: str,
        to_peer_id: str,
        signal_data: dict
    ):
        """
        Reenvía señales WebRTC entre peers
        """
        message = {
            "type": "webrtc_signal",
            "from_peer_id": from_peer_id,
            "signal": signal_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.send_personal_message(message, room_id, to_peer_id)

    def get_room_peers(self, room_id: str) -> List[str]:
        """Obtiene la lista de peers en un room"""
        if room_id in self.active_connections:
            return list(self.active_connections[room_id].keys())
        return []

    def get_active_rooms(self) -> List[str]:
        """Obtiene la lista de rooms activos"""
        return list(self.active_connections.keys())

    async def handle_webrtc_signaling(
        self,
        websocket: WebSocket,
        room_id: str,
        peer_id: str
    ):
        """
        Maneja el ciclo de vida de señalización WebRTC para un peer
        """
        try:
            await self.connect(websocket, room_id, peer_id)

            # Enviar lista de peers actuales
            peers = self.get_room_peers(room_id)
            await websocket.send_json({
                "type": "room_state",
                "peers": [p for p in peers if p != peer_id],
                "your_peer_id": peer_id
            })

            # Loop principal de mensajes
            while True:
                data = await websocket.receive_json()

                message_type = data.get("type")

                if message_type == "offer" or message_type == "answer":
                    # Reenviar offer/answer al peer destinatario
                    target_peer = data.get("target_peer_id")
                    if target_peer:
                        await self.forward_signal(
                            room_id,
                            peer_id,
                            target_peer,
                            data
                        )

                elif message_type == "ice_candidate":
                    # Reenviar ICE candidate
                    target_peer = data.get("target_peer_id")
                    if target_peer:
                        await self.forward_signal(
                            room_id,
                            peer_id,
                            target_peer,
                            data
                        )

                elif message_type == "broadcast":
                    # Broadcast a todos en el room
                    await self.broadcast_to_room(
                        room_id,
                        {
                            "type": "broadcast_message",
                            "from_peer_id": peer_id,
                            "data": data.get("data"),
                            "timestamp": datetime.utcnow().isoformat()
                        },
                        exclude_peer=peer_id
                    )

        except WebSocketDisconnect:
            await self.disconnect(room_id, peer_id)
        except Exception as e:
            print(f"Error en WebSocket: {e}")
            await self.disconnect(room_id, peer_id)


# Instancia global del gestor
manager = ConnectionManager()
