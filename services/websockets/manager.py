from collections import defaultdict

from fastapi import WebSocket
from starlette.websockets import WebSocketState
from utils.colored_logger import get_logger


class ConnectionManager:
    """Tracks active websocket connections grouped by conversation id."""

    def __init__(self) -> None:
        self._rooms: dict[str, set[WebSocket]] = defaultdict(set)
        self._logger = get_logger("WebSocket >> Manager")

    async def connect(self, conversation_id: str, websocket: WebSocket) -> None:
        if websocket.client_state != WebSocketState.CONNECTED:
            await websocket.accept()
        self._rooms[conversation_id].add(websocket)
        self._logger.debug(
            "Connected socket to room conversation_id=%s active_connections=%s",
            conversation_id,
            len(self._rooms[conversation_id]),
        )

    def disconnect(self, conversation_id: str, websocket: WebSocket) -> None:
        room = self._rooms.get(conversation_id)
        if not room:
            self._logger.debug("Disconnect ignored for missing room conversation_id=%s", conversation_id)
            return
        room.discard(websocket)
        if not room:
            self._rooms.pop(conversation_id, None)
            self._logger.debug("Removed empty room conversation_id=%s", conversation_id)
            return
        self._logger.debug(
            "Disconnected socket from room conversation_id=%s active_connections=%s",
            conversation_id,
            len(room),
        )

    async def broadcast(self, conversation_id: str, message: str) -> None:
        sockets = list(self._rooms.get(conversation_id, ()))
        if not sockets:
            self._logger.debug("Broadcast skipped; no sockets for conversation_id=%s", conversation_id)
            return

        self._logger.debug(
            "Broadcasting message to room conversation_id=%s recipients=%s",
            conversation_id,
            len(sockets),
        )
        for socket in sockets:
            await socket.send_text(message)


manager = ConnectionManager()
