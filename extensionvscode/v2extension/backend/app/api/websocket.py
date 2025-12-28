"""WebSocket endpoint for real-time communication."""

import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.websocket import connection_manager, WebSocketMessage
from app.services.message_router import MessageRouter

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """
    Main WebSocket endpoint for real-time communication.

    Client connects with: ws://host:port/api/v1/ws?token=<jwt_token>
    """
    # Authenticate connection
    user_id = await connection_manager.authenticate(websocket)
    if not user_id:
        logger.warning("WebSocket authentication failed")
        return

    # Accept and register connection
    connection_id = await connection_manager.connect(websocket, user_id)

    # Send welcome message
    welcome_msg = WebSocketMessage(
        type="connection.established",
        payload={
            "connection_id": connection_id,
            "user_id": user_id,
            "message": "Connected to AI Goals Tracker"
        }
    )
    await connection_manager.send_personal_message(welcome_msg, connection_id)

    # Initialize message router
    router_instance = MessageRouter(connection_id, user_id, connection_manager)

    try:
        # Listen for messages
        while True:
            # Receive message
            data = await websocket.receive_text()

            # Parse message
            try:
                message = WebSocketMessage.from_json(data)
            except Exception as e:
                logger.error(f"Failed to parse message: {e}")
                error_msg = WebSocketMessage(
                    type="error",
                    payload={"error": "Invalid message format"}
                )
                await connection_manager.send_personal_message(error_msg, connection_id)
                continue

            # Route message to appropriate handler
            await router_instance.route_message(message)

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {connection_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await connection_manager.disconnect(connection_id)
