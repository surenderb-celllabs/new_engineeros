from __future__ import annotations

import re
from collections import defaultdict
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path
from uuid import NAMESPACE_URL, uuid4, uuid5

import yaml
from sqlalchemy import select
from sqlalchemy.orm import Session

from services.api.projects.crud import get_project_by_id
from services.api.projects.services import can_access_workspace
from services.api.sessions.crud import (
    get_next_session_version_number,
    get_phase_state,
    get_session_version,
    list_session_versions_for_session,
    list_phase_states,
    list_session_versions,
    save_phase_state,
    save_session_version,
)
from services.api.sessions.model import ProjectPhaseState, ProjectSessionVersion
from services.api.sessions.schema import (
    DocumentNode,
    FileContentResponse,
    FileVersionsResponse,
    PhaseDocumentsResponse,
    PhaseStatusResponse,
    PhaseWithSessionStatusResponse,
    ProjectDocumentTreeResponse,
    ProjectWorkflowStatusResponse,
    SessionVersionHistoryResponse,
    SessionDocumentsResponse,
    SessionDocumentsNode,
    SessionStatusResponse,
    SessionVersionResponse,
)
from services.api.users.model import User
from services.core.config import settings
from services.core.exceptions import PermissionDeniedError, ResourceNotFoundError
from services.core.minio import MinioService


PHASES_YAML_PATH = Path(__file__).resolve().parents[3] / "phases_and_sessions.yaml"


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower()).strip("_")
    return slug or "session"


@lru_cache(maxsize=1)
def load_phase_session_config() -> dict[str, list[dict[str, str]]]:
    if not PHASES_YAML_PATH.exists():
        return {}

    with PHASES_YAML_PATH.open("r", encoding="utf-8") as fp:
        payload = yaml.safe_load(fp) or {}

    phases = payload.get("phases", {})
    normalized: dict[str, list[dict[str, str]]] = {}
    for phase_id, sessions in phases.items():
        counters: dict[str, int] = {}
        normalized_sessions: list[dict[str, str]] = []
        for title in sessions or []:
            base = _slugify(str(title))
            counters[base] = counters.get(base, 0) + 1
            session_id = f"{base}_{counters[base]}" if counters[base] > 1 else base
            normalized_sessions.append({"session_id": session_id, "session_title": str(title)})
        normalized[str(phase_id)] = normalized_sessions
    return normalized


def _assert_project_access(db: Session, project_id: str, current_user: User):
    project = get_project_by_id(db, project_id)
    if project is None:
        raise ResourceNotFoundError("Project not found")

    can_access = can_access_workspace(project.workspace, current_user) or any(
        member.id == current_user.id for member in project.members
    )
    if not can_access:
        raise PermissionDeniedError("Access denied to project")
    return project


def _phase_uuid(project_id: str, phase_key: str) -> str:
    return str(uuid5(NAMESPACE_URL, f"{project_id}:phase:{phase_key}"))


def _session_uuid(project_id: str, phase_key: str, session_key: str) -> str:
    return str(uuid5(NAMESPACE_URL, f"{project_id}:phase:{phase_key}:session:{session_key}"))


def _phase_key_from_id(project_id: str, phase_id: str) -> str:
    for phase_key in load_phase_session_config().keys():
        if _phase_uuid(project_id, phase_key) == phase_id:
            return phase_key
    raise ResourceNotFoundError(f"Phase '{phase_id}' not found")


def _session_details_from_ids(project_id: str, phase_id: str, session_id: str) -> tuple[str, str]:
    config = load_phase_session_config()
    phase_key = _phase_key_from_id(project_id, phase_id)
    for session in config.get(phase_key, []):
        session_key = session["session_id"]
        if _session_uuid(project_id, phase_key, session_key) == session_id:
            return session_key, session["session_title"]
    raise ResourceNotFoundError(f"Session '{session_id}' not found in phase '{phase_id}'")


def _assert_phase_exists(project_id: str, phase_id: str) -> str:
    return _phase_key_from_id(project_id, phase_id)


def _safe_filename(filename: str) -> str:
    cleaned = filename.strip().replace("\\", "/").split("/")[-1]
    if not cleaned:
        raise ResourceNotFoundError("Invalid filename")
    return cleaned


def _object_key(workspace_id: str, project_id: str, phase_id: str, session_id: str, filename: str) -> str:
    safe_name = _safe_filename(filename)
    return f"{workspace_id}/{project_id}/{phase_id}/{session_id}/documents/{safe_name}"


def _phase_documents_link(project_id: str, phase_id: str) -> str:
    return f"{settings.API_PREFIX}/users/projects/{project_id}/phases/{phase_id}/documents"


def _session_documents_link(project_id: str, phase_id: str, session_id: str) -> str:
    return f"{settings.API_PREFIX}/users/projects/{project_id}/phases/{phase_id}/sessions/{session_id}/documents"


def _session_version_to_response(db: Session, row: ProjectSessionVersion) -> SessionVersionResponse:
    approved_by_email = None
    if row.approved_by_user_id is not None:
        approved_by_user = db.get(User, row.approved_by_user_id)
        approved_by_email = approved_by_user.email if approved_by_user else None

    return SessionVersionResponse(
        id=row.id,
        project_id=row.project_id,
        phase_id=row.phase_id,
        session_id=row.session_id,
        session_title=row.session_title,
        version=row.version,
        conversation_id=row.conversation_id,
        approval_status=row.approval_status,
        remark=row.remark,
        output=row.output,
        approved_at=row.approved_at,
        approved_by=approved_by_email,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def create_text_document(
    db: Session,
    minio: MinioService,
    project_id: str,
    phase_id: str,
    session_id: str,
    filename: str,
    content: str,
    current_user: User,
) -> dict:
    project = _assert_project_access(db, project_id, current_user)
    _assert_phase_exists(project_id, phase_id)
    _session_details_from_ids(project_id, phase_id, session_id)

    bucket = minio.ensure_user_bucket(current_user.id)
    key = _object_key(project.workspace_id, project.id, phase_id, session_id, filename)
    version_id = minio.put_bytes_object(
        bucket=bucket,
        object_key=key,
        payload=content.encode("utf-8"),
        content_type="text/plain; charset=utf-8",
    )
    return {
        "filename": _safe_filename(filename),
        "object_key": key,
        "version_id": version_id,
        "download_url": minio.presigned_download_url(bucket, key, version_id=version_id),
    }


def upload_document_file(
    db: Session,
    minio: MinioService,
    project_id: str,
    phase_id: str,
    session_id: str,
    filename: str,
    payload: bytes,
    content_type: str | None,
    current_user: User,
) -> dict:
    project = _assert_project_access(db, project_id, current_user)
    _assert_phase_exists(project_id, phase_id)
    _session_details_from_ids(project_id, phase_id, session_id)

    bucket = minio.ensure_user_bucket(current_user.id)
    key = _object_key(project.workspace_id, project.id, phase_id, session_id, filename)
    version_id = minio.put_bytes_object(bucket=bucket, object_key=key, payload=payload, content_type=content_type)
    return {
        "filename": _safe_filename(filename),
        "object_key": key,
        "version_id": version_id,
        "download_url": minio.presigned_download_url(bucket, key, version_id=version_id),
    }


def get_document_versions(
    db: Session,
    minio: MinioService,
    project_id: str,
    phase_id: str,
    session_id: str,
    filename: str,
    current_user: User,
) -> FileVersionsResponse:
    project = _assert_project_access(db, project_id, current_user)
    _assert_phase_exists(project_id, phase_id)
    _session_details_from_ids(project_id, phase_id, session_id)

    bucket = minio.ensure_user_bucket(current_user.id)
    key = _object_key(project.workspace_id, project.id, phase_id, session_id, filename)
    versions = minio.list_object_versions(bucket=bucket, object_key=key)
    return FileVersionsResponse(filename=_safe_filename(filename), versions=versions)


def get_document_content_by_version(
    db: Session,
    minio: MinioService,
    project_id: str,
    phase_id: str,
    session_id: str,
    filename: str,
    version_id: str,
    current_user: User,
) -> FileContentResponse:
    project = _assert_project_access(db, project_id, current_user)
    _assert_phase_exists(project_id, phase_id)
    _session_details_from_ids(project_id, phase_id, session_id)

    bucket = minio.ensure_user_bucket(current_user.id)
    key = _object_key(project.workspace_id, project.id, phase_id, session_id, filename)
    body = minio.get_object_bytes(bucket=bucket, object_key=key, version_id=version_id)
    return FileContentResponse(
        filename=_safe_filename(filename),
        version_id=version_id,
        content=body.decode("utf-8"),
    )


def _documents_from_prefix(minio: MinioService, bucket: str, prefix: str) -> dict[str, dict[str, list[DocumentNode]]]:
    grouped: dict[str, dict[str, list[DocumentNode]]] = defaultdict(lambda: defaultdict(list))
    objects = minio.list_objects(bucket=bucket, prefix=prefix, recursive=True)

    for obj in objects:
        object_name = obj["object_name"]
        parts = object_name.split("/")
        if len(parts) < 6 or parts[4] != "documents":
            continue

        phase_id = parts[2]
        session_id = parts[3]
        filename = "/".join(parts[5:])
        versions = minio.list_object_versions(bucket, object_name)
        latest = versions[0] if versions else {"version_id": None, "last_modified": obj.get("last_modified")}
        version_id = latest.get("version_id")
        current_version = len(versions) if versions else None

        grouped[phase_id][session_id].append(
            DocumentNode(
                filename=filename,
                object_key=object_name,
                current_version=current_version,
                current_version_id=version_id,
                version_id=version_id,
                last_modified=latest.get("last_modified"),
                download_url=minio.presigned_download_url(bucket, object_name, version_id=version_id),
            )
        )

    for phase_map in grouped.values():
        for docs in phase_map.values():
            docs.sort(key=lambda d: d.filename.lower())
    return grouped


def get_project_document_tree(
    db: Session,
    minio: MinioService,
    project_id: str,
    current_user: User,
) -> ProjectDocumentTreeResponse:
    project = _assert_project_access(db, project_id, current_user)
    bucket = minio.ensure_user_bucket(current_user.id)
    prefix = f"{project.workspace_id}/{project.id}/"
    grouped = _documents_from_prefix(minio, bucket, prefix)

    phases = []
    for phase_id in sorted(grouped.keys()):
        sessions = []
        for session_id in sorted(grouped[phase_id].keys()):
            sessions.append(SessionDocumentsNode(session_id=session_id, documents=grouped[phase_id][session_id]))
        phases.append({"phase_id": phase_id, "sessions": sessions})

    return ProjectDocumentTreeResponse(project_id=project.id, phases=phases)


def get_phase_documents(
    db: Session,
    minio: MinioService,
    project_id: str,
    phase_id: str,
    current_user: User,
) -> PhaseDocumentsResponse:
    project = _assert_project_access(db, project_id, current_user)
    _assert_phase_exists(project_id, phase_id)

    bucket = minio.ensure_user_bucket(current_user.id)
    prefix = f"{project.workspace_id}/{project.id}/{phase_id}/"
    grouped = _documents_from_prefix(minio, bucket, prefix)

    sessions = []
    for session_id in sorted(grouped.get(phase_id, {}).keys()):
        sessions.append(SessionDocumentsNode(session_id=session_id, documents=grouped[phase_id][session_id]))

    return PhaseDocumentsResponse(project_id=project.id, phase_id=phase_id, sessions=sessions)


def get_session_documents(
    db: Session,
    minio: MinioService,
    project_id: str,
    phase_id: str,
    session_id: str,
    current_user: User,
) -> SessionDocumentsResponse:
    project = _assert_project_access(db, project_id, current_user)
    _assert_phase_exists(project_id, phase_id)
    _session_details_from_ids(project_id, phase_id, session_id)

    bucket = minio.ensure_user_bucket(current_user.id)
    prefix = f"{project.workspace_id}/{project.id}/{phase_id}/{session_id}/"
    grouped = _documents_from_prefix(minio, bucket, prefix)
    session_docs = grouped.get(phase_id, {}).get(session_id, [])
    return SessionDocumentsResponse(project_id=project.id, phase_id=phase_id, session_id=session_id, documents=session_docs)


def initialize_project_workflow(
    db: Session,
    project_id: str,
    created_by_user_id: int,
) -> None:
    config = load_phase_session_config()
    touched = False

    for phase_key, sessions in config.items():
        phase_id = _phase_uuid(project_id, phase_key)
        phase_row = get_phase_state(db, project_id, phase_id)
        if phase_row is None:
            phase_row = ProjectPhaseState(
                project_id=project_id,
                phase_id=phase_id,
                approval_status="pending",
            )
            db.add(phase_row)
            touched = True

        for session in sessions:
            session_id = _session_uuid(project_id, phase_key, session["session_id"])
            next_version = get_next_session_version_number(db, project_id, phase_id, session_id)
            if next_version != 1:
                continue
            db.add(
                ProjectSessionVersion(
                    project_id=project_id,
                    phase_id=phase_id,
                    session_id=session_id,
                    session_title=session["session_title"],
                    version=1,
                    conversation_id=str(uuid4()),
                    approval_status="pending",
                    created_by_user_id=created_by_user_id,
                )
            )
            touched = True

    if touched:
        db.commit()


def create_new_session_version(
    db: Session,
    project_id: str,
    phase_id: str,
    session_id: str,
    remark: str | None,
    current_user: User,
) -> SessionVersionResponse:
    _assert_project_access(db, project_id, current_user)
    _assert_phase_exists(project_id, phase_id)
    _, session_title = _session_details_from_ids(project_id, phase_id, session_id)

    row = ProjectSessionVersion(
        project_id=project_id,
        phase_id=phase_id,
        session_id=session_id,
        session_title=session_title,
        version=get_next_session_version_number(db, project_id, phase_id, session_id),
        conversation_id=str(uuid4()),
        approval_status="pending",
        remark=remark,
        created_by_user_id=current_user.id,
    )
    row = save_session_version(db, row)
    return _session_version_to_response(db, row)


def rename_session_title(
    db: Session,
    project_id: str,
    phase_id: str,
    session_id: str,
    session_title: str,
    current_user: User,
) -> SessionVersionResponse:
    _assert_project_access(db, project_id, current_user)
    _assert_phase_exists(project_id, phase_id)
    _session_details_from_ids(project_id, phase_id, session_id)

    rows = list_session_versions_for_session(db, project_id, phase_id, session_id)
    if not rows:
        raise ResourceNotFoundError("Session not found")

    for row in rows:
        row.session_title = session_title
        row.updated_at = datetime.now(UTC)

    db.commit()
    db.refresh(rows[0])
    return _session_version_to_response(db, rows[0])


def get_session_version_history(
    db: Session,
    project_id: str,
    phase_id: str,
    session_id: str,
    current_user: User,
    previous_only: bool = True,
) -> SessionVersionHistoryResponse:
    project = _assert_project_access(db, project_id, current_user)
    initialize_project_workflow(db, project_id, project.owner_id)
    _assert_phase_exists(project_id, phase_id)
    _session_details_from_ids(project_id, phase_id, session_id)

    rows = list_session_versions_for_session(db, project_id, phase_id, session_id)
    if previous_only and rows:
        rows = rows[1:]

    return SessionVersionHistoryResponse(
        project_id=project_id,
        phase_id=phase_id,
        session_id=session_id,
        versions=[_session_version_to_response(db, row) for row in rows],
    )


def approve_phase(
    db: Session,
    project_id: str,
    phase_id: str,
    remark: str | None,
    current_user: User,
) -> PhaseStatusResponse:
    _assert_project_access(db, project_id, current_user)
    phase_key = _assert_phase_exists(project_id, phase_id)

    row = get_phase_state(db, project_id, phase_id)
    if row is None:
        row = ProjectPhaseState(project_id=project_id, phase_id=phase_id)

    row.approval_status = "approved"
    row.remark = remark
    row.approved_at = datetime.now(UTC)
    row.approved_by_user_id = current_user.id
    row = save_phase_state(db, row)

    return PhaseStatusResponse(
        phase_id=row.phase_id,
        phase_title=phase_key,
        approval_status=row.approval_status,
        remark=row.remark,
        approved_at=row.approved_at,
        approved_by=current_user.email,
        documents_link=_phase_documents_link(project_id, phase_id),
    )


def approve_session_version(
    db: Session,
    project_id: str,
    phase_id: str,
    session_id: str,
    version: int,
    remark: str | None,
    current_user: User,
) -> SessionVersionResponse:
    _assert_project_access(db, project_id, current_user)
    _assert_phase_exists(project_id, phase_id)
    _session_details_from_ids(project_id, phase_id, session_id)

    row = get_session_version(db, project_id, phase_id, session_id, version)
    if row is None:
        raise ResourceNotFoundError("Session version not found")

    row.approval_status = "approved"
    row.remark = remark
    row.approved_at = datetime.now(UTC)
    row.approved_by_user_id = current_user.id
    row = save_session_version(db, row)
    return _session_version_to_response(db, row)


def get_project_phase_session_status(db: Session, project_id: str, current_user: User) -> ProjectWorkflowStatusResponse:
    project = _assert_project_access(db, project_id, current_user)
    initialize_project_workflow(db, project_id, project.owner_id)
    config = load_phase_session_config()

    phase_rows = list_phase_states(db, project_id)
    phase_map = {row.phase_id: row for row in phase_rows}

    session_rows = list_session_versions(db, project_id)
    latest_sessions: dict[tuple[str, str], ProjectSessionVersion] = {}
    for row in session_rows:
        key = (row.phase_id, row.session_id)
        if key not in latest_sessions or row.version > latest_sessions[key].version:
            latest_sessions[key] = row

    user_ids = {row.approved_by_user_id for row in phase_rows if row.approved_by_user_id}
    user_ids.update(row.approved_by_user_id for row in latest_sessions.values() if row.approved_by_user_id)
    user_map = (
        {user.id: user.email for user in db.execute(select(User).where(User.id.in_(list(user_ids)))).scalars().all()}
        if user_ids
        else {}
    )

    response_phases: list[PhaseWithSessionStatusResponse] = []
    for phase_key, sessions in config.items():
        phase_id = _phase_uuid(project_id, phase_key)
        phase_row = phase_map.get(phase_id)
        phase_status = PhaseStatusResponse(
            phase_id=phase_id,
            phase_title=phase_key,
            approval_status=phase_row.approval_status if phase_row else "pending",
            remark=phase_row.remark if phase_row else None,
            approved_at=phase_row.approved_at if phase_row else None,
            approved_by=user_map.get(phase_row.approved_by_user_id) if phase_row and phase_row.approved_by_user_id else None,
            documents_link=_phase_documents_link(project_id, phase_id),
        )

        session_statuses: list[SessionStatusResponse] = []
        for session in sessions:
            session_id = _session_uuid(project_id, phase_key, session["session_id"])
            latest = latest_sessions.get((phase_id, session_id))
            session_statuses.append(
                SessionStatusResponse(
                    session_id=session_id,
                    session_title=session["session_title"],
                    latest_version=latest.version if latest else None,
                    approval_status=latest.approval_status if latest else "pending",
                    remark=latest.remark if latest else None,
                    approved_at=latest.approved_at if latest else None,
                    approved_by=user_map.get(latest.approved_by_user_id) if latest and latest.approved_by_user_id else None,
                    documents_link=_session_documents_link(project_id, phase_id, session_id),
                )
            )

        response_phases.append(PhaseWithSessionStatusResponse(phase=phase_status, sessions=session_statuses))

    return ProjectWorkflowStatusResponse(project_id=project_id, phases=response_phases)
