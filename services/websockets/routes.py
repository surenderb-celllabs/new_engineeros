import os
from importlib import import_module
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from langchain_core.messages import HumanMessage
from langchain_ollama.embeddings import OllamaEmbeddings
from sqlalchemy import select
from uuid import NAMESPACE_URL, uuid5
from dotenv import load_dotenv

from services.api.sessions.model import ProjectSessionVersion
from services.api.sessions.services import load_phase_session_config
from services.api.users.crud import get_user_by_email
from services.core.config import settings
from services.core.database import SessionLocal
from services.core.exceptions import AuthError
from services.core.security import decode_access_token
from services.websockets.manager import manager
from utils.colored_logger import get_logger


router = APIRouter(prefix="/ws", tags=["websockets"])
logger = get_logger("WebSocket >> Routes")
load_dotenv()


def _mask_token(token: str | None) -> str:
    if not token:
        return "none"
    if len(token) <= 12:
        return "***"
    return f"{token[:6]}...{token[-6:]}"


async def _close_socket(websocket: WebSocket, code: int, reason: str, *, conversation_id: str) -> None:
    logger.warning(
        "Closing websocket conversation_id=%s code=%s reason=%s",
        conversation_id,
        code,
        reason,
    )
    await websocket.close(code=code, reason=reason)


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


def _get_pgvector_connection_string() -> str:
    url = os.getenv("VECTOR_DB_URL") or os.getenv("DATABASE_URL") or settings.DATABASE_URL

    if url.startswith("sqlite"):
        raise ValueError(
            "PGVector requires PostgreSQL, but got SQLite URL. "
            "Set VECTOR_DB_URL (or DATABASE_URL) to a PostgreSQL connection string."
        )

    if not url.startswith("postgresql"):
        raise ValueError(
            "Unsupported vector DB URL scheme. Expected postgresql:// or postgresql+driver://"
        )

    if url.startswith("postgresql+asyncpg://"):
        return url.replace("postgresql+asyncpg://", "postgresql+psycopg://", 1)
    return url


def _build_vector_store(phase_number: int, session_number: int, project_id: str) -> Any:
    collection_name = f"{project_id}_phase_{phase_number}_session_{session_number}".replace("-", "_")
    embeddings = OllamaEmbeddings(
        model=os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text:latest"),
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    )
    connection_string = _get_pgvector_connection_string()

    try:
        from langchain_postgres import PGVector

        return PGVector(
            embeddings=embeddings,
            collection_name=collection_name,
            connection=connection_string,
            use_jsonb=True,
        )
    except ImportError:
        from langchain_community.vectorstores import PGVector

        return PGVector(
            connection_string=connection_string,
            embedding_function=embeddings,
            collection_name=collection_name,
        )


def _load_graph_for_phase_session(
    phase_number: int,
    session_number: int,
    *,
    project_id: str,
) -> Any:
    if phase_number != 5:
        raise ValueError(f"Unsupported phase '{phase_number}' for websocket graph execution")

    session_map: dict[int, tuple[str, bool]] = {
        1: ("app.phase_5.session_01.graph", False),
        2: ("app.phase_5.session_02.graph", False),
        3: ("app.phase_5.session_03.graph", True),
        4: ("app.phase_5.session_04.graph", False),
        5: ("app.phase_5.session_05.graph", False),
    }
    mapping = session_map.get(session_number)
    if mapping is None:
        raise ValueError(f"Unsupported session '{session_number}' for phase '{phase_number}'")

    module_path, needs_user_story_ids = mapping
    graph_module = import_module(module_path)
    vector_store = _build_vector_store(
        phase_number=phase_number,
        session_number=session_number,
        project_id=project_id,
    )

    if needs_user_story_ids:
        return graph_module.IdeaExpansion(vector_store=vector_store, user_stories_ids=[]).compile()
    return graph_module.IdeaExpansion(vector_store=vector_store).compile()


async def _graph_output_from_compiled_graph(
    graph: Any,
    message: str,
    *,
    conversation_id: str,
) -> None:
    logger.debug("Starting graph stream for conversation_id=%s", conversation_id)
    graph_input = {
        "messages": [HumanMessage(content=message)],
        "convo_end": False,
        "us_ids": [],
        "us_category": "",
        "total_frs": 0,
        "total_nfrs": 0,
    }
    config = {
        "recursion_limit": 50,
        "configurable": {"thread_id": conversation_id},
    }

    async def _run_stream() -> None:
        for mode, chunks, meta in graph.stream(
            input=graph_input,
            config=config,
            subgraphs=True,
            stream_mode=["custom"],
        ):
            if isinstance(meta, dict) and meta.get("resp_type") == "options":
                logger.debug("Skipping options response in stream for conversation_id=%s", conversation_id)
                continue

            messages = meta.get("messages") if isinstance(meta, dict) else None
            if messages:
                content = getattr(messages[-1], "content", "")
                if content:
                    logger.debug("Streaming content chunk for conversation_id=%s", conversation_id)
                    await manager.broadcast(conversation_id=conversation_id, message=content)

    await _run_stream()
    logger.debug("Completed graph stream for conversation_id=%s", conversation_id)


@router.websocket("/conversations/{conversation_id}")
async def conversation_socket(websocket: WebSocket, conversation_id: str) -> None:
    logger.info(
        "WebSocket connection requested for conversation_id=%s client=%s",
        conversation_id,
        websocket.client,
    )
    await websocket.accept()
    logger.debug("WebSocket accepted for conversation_id=%s", conversation_id)

    token = _extract_bearer_token(websocket)
    logger.debug(
        "Extracted token for conversation_id=%s token=%s",
        conversation_id,
        _mask_token(token),
    )
    if token is None:
        await _close_socket(
            websocket,
            status.WS_1008_POLICY_VIOLATION,
            "Missing bearer token",
            conversation_id=conversation_id,
        )
        return

    db = SessionLocal()
    try:
        logger.debug("Decoding access token for conversation_id=%s", conversation_id)
        payload = decode_access_token(token)
        email = payload.get("sub")
        if not email:
            raise AuthError("Invalid token subject")

        logger.debug("Looking up user by email=%s", email)
        user = get_user_by_email(db, email)
        if user is None:
            raise AuthError("User no longer exists")

        logger.debug("Fetching session version for conversation_id=%s", conversation_id)
        stmt = select(ProjectSessionVersion).where(ProjectSessionVersion.conversation_id == conversation_id)
        session_version = db.execute(stmt).scalar_one_or_none()
        if session_version is None:
            await _close_socket(
                websocket,
                status.WS_1008_POLICY_VIOLATION,
                "Conversation not found",
                conversation_id=conversation_id,
            )
            return

        if session_version.created_by_user_id != user.id:
            logger.warning(
                "Forbidden websocket access for conversation_id=%s user_id=%s owner_id=%s",
                conversation_id,
                user.id,
                session_version.created_by_user_id,
            )
            await _close_socket(
                websocket,
                status.WS_1008_POLICY_VIOLATION,
                "Forbidden for this conversation",
                conversation_id=conversation_id,
            )
            return
    except AuthError as exc:
        logger.warning("Auth failure for conversation_id=%s detail=%s", conversation_id, str(exc))
        await _close_socket(
            websocket,
            status.WS_1008_POLICY_VIOLATION,
            "Invalid or expired token",
            conversation_id=conversation_id,
        )
        return
    except Exception:
        logger.exception("Unexpected error during websocket auth for conversation_id=%s", conversation_id)
        await _close_socket(
            websocket,
            status.WS_1011_INTERNAL_ERROR,
            "Authentication failure",
            conversation_id=conversation_id,
        )
        return
    finally:
        db.close()
        logger.debug("Closed DB session for conversation_id=%s", conversation_id)

    phase_session = _derive_phase_session_numbers(session_version)
    if phase_session is None:
        await _close_socket(
            websocket,
            status.WS_1008_POLICY_VIOLATION,
            "Unable to resolve phase/session for this conversation",
            conversation_id=conversation_id,
        )
        return

    phase_number, session_number = phase_session
    logger.info(
        "Resolved phase/session for conversation_id=%s phase=%s session=%s",
        conversation_id,
        phase_number,
        session_number,
    )
    try:
        logger.debug("Initializing graph for conversation_id=%s", conversation_id)
        graph = _load_graph_for_phase_session(
            phase_number=phase_number,
            session_number=session_number,
            project_id=session_version.project_id,
        )
        logger.success("Graph initialized for conversation_id=%s", conversation_id)
    except Exception as exc:
        logger.exception("Graph initialization failed for conversation_id=%s", conversation_id)
        await _close_socket(
            websocket,
            status.WS_1011_INTERNAL_ERROR,
            f"Unable to initialize graph: {exc}",
            conversation_id=conversation_id,
        )
        return

    await manager.connect(conversation_id=conversation_id, websocket=websocket)
    logger.info("WebSocket connected to room conversation_id=%s", conversation_id)
    await websocket.send_text(f"phase: {phase_number}, session: {session_number}")
    try:
        while True:
            message = await websocket.receive_text()
            logger.debug("Received websocket message for conversation_id=%s", conversation_id)
            await _graph_output_from_compiled_graph(
                graph=graph,
                message=message,
                conversation_id=conversation_id,
            )
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected for conversation_id=%s", conversation_id)
        manager.disconnect(conversation_id=conversation_id, websocket=websocket)
    except Exception:
        logger.exception("Unhandled websocket error for conversation_id=%s", conversation_id)
        manager.disconnect(conversation_id=conversation_id, websocket=websocket)
