from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from sqlalchemy import select
from uuid import NAMESPACE_URL, uuid5

from services.api.sessions.model import ProjectSessionVersion
from services.api.sessions.services import load_phase_session_config
from services.api.users.crud import get_user_by_email
from services.core.database import SessionLocal
from services.core.exceptions import AuthError
from services.core.security import decode_access_token
from services.websockets.manager import manager


router = APIRouter(prefix="/ws", tags=["websockets"])


def _extract_bearer_token(websocket: WebSocket) -> str | None:
    token = websocket.query_params.get("token")
    if token:
        return token

    authorization = websocket.headers.get("authorization")
    if not authorization:
        return None

    scheme, _, credentials = authorization.partition(" ")
    if scheme.lower() != "bearer" or not credentials:
        return None
    return credentials


def _extract_phase_number(phase_key: str, default_index: int) -> int:
    if "_" in phase_key:
        suffix = phase_key.rsplit("_", 1)[-1]
        if suffix.isdigit():
            return int(suffix)
    return default_index


def _derive_phase_session_numbers(row: ProjectSessionVersion) -> tuple[int, int] | None:
    config = load_phase_session_config()
    for phase_index, (phase_key, sessions) in enumerate(config.items(), start=1):
        phase_id = str(uuid5(NAMESPACE_URL, f"{row.project_id}:phase:{phase_key}"))
        if phase_id != row.phase_id:
            continue

        phase_number = _extract_phase_number(phase_key, phase_index)
        for session_index, session in enumerate(sessions, start=1):
            session_key = session["session_id"]
            session_id = str(uuid5(NAMESPACE_URL, f"{row.project_id}:phase:{phase_key}:session:{session_key}"))
            if session_id == row.session_id:
                return phase_number, session_index
        return None

    return None


@router.websocket("/conversations/{conversation_id}")
async def conversation_socket(websocket: WebSocket, conversation_id: str) -> None:
    token = _extract_bearer_token(websocket)
    if token is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Missing bearer token")
        return

    db = SessionLocal()
    try:
        payload = decode_access_token(token)
        email = payload.get("sub")
        if not email:
            raise AuthError("Invalid token subject")

        user = get_user_by_email(db, email)
        if user is None:
            raise AuthError("User no longer exists")

        stmt = select(ProjectSessionVersion).where(ProjectSessionVersion.conversation_id == conversation_id)
        session_version = db.execute(stmt).scalar_one_or_none()
        if session_version is None:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Conversation not found")
            return

        if session_version.created_by_user_id != user.id:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Forbidden for this conversation")
            return
    except AuthError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid or expired token")
        return
    finally:
        db.close()

    phase_session = _derive_phase_session_numbers(session_version)
    if phase_session is None:
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Unable to resolve phase/session for this conversation",
        )
        return

    await manager.connect(conversation_id=conversation_id, websocket=websocket)
    phase_number, session_number = phase_session
    await websocket.send_text(f"phase: {phase_number}, session: {session_number}")
    try:
        while True:
            message = await websocket.receive_text()
            await manager.broadcast(conversation_id=conversation_id, message=message)
    except WebSocketDisconnect:
        manager.disconnect(conversation_id=conversation_id, websocket=websocket)
