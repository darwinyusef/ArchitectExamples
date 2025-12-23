from fastapi import APIRouter, WebSocket, Query
from app.services.websocket_service import manager

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: str,
    peer_id: str = Query(..., description="ID único del peer")
):
    """
    WebSocket endpoint para señalización WebRTC
    Permite comunicación peer-to-peer a través del servidor

    Parámetros:
    - room_id: ID de la sala de comunicación
    - peer_id: ID único del cliente/peer
    """
    await manager.handle_webrtc_signaling(websocket, room_id, peer_id)


@router.get("/rooms", tags=["rooms"])
async def get_active_rooms():
    """
    Obtiene la lista de rooms activos
    """
    rooms = manager.get_active_rooms()
    return {
        "rooms": rooms,
        "total": len(rooms)
    }


@router.get("/rooms/{room_id}/peers", tags=["rooms"])
async def get_room_peers(room_id: str):
    """
    Obtiene la lista de peers en un room específico
    """
    peers = manager.get_room_peers(room_id)
    return {
        "room_id": room_id,
        "peers": peers,
        "total": len(peers)
    }
