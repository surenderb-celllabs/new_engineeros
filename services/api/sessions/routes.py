from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from services.api.sessions.schema import (
    CreateTextDocumentRequest,
    FileContentResponse,
    FileVersionsResponse,
    PhaseDocumentsResponse,
    PhaseStatusResponse,
    ProjectDocumentTreeResponse,
    ProjectWorkflowStatusResponse,
    RemarkRequest,
    SessionRenameRequest,
    SessionVersionCreateRequest,
    SessionDocumentsResponse,
    SessionVersionHistoryResponse,
    SessionVersionResponse,
    UploadedDocumentResponse,
)
from services.api.sessions.services import (
    approve_phase,
    approve_session_version,
    create_new_session_version,
    create_text_document,
    get_document_content_by_version,
    get_document_versions,
    get_phase_documents,
    get_session_documents,
    get_project_document_tree,
    get_project_phase_session_status,
    get_session_version_history,
    rename_session_title,
    upload_document_file,
)
from services.api.users.model import User
from services.core.database import get_db
from services.core.exceptions import PermissionDeniedError, ResourceNotFoundError
from services.dependencies.auth import get_current_user
from services.dependencies.minio import get_minio_service


router = APIRouter(prefix="/users", tags=["sessions"])


@router.post(
    "/projects/{project_id}/phases/{phase_id}/sessions/{session_id}/documents/text",
    response_model=UploadedDocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_document_from_text(
    project_id: str,
    phase_id: str,
    session_id: str,
    payload: CreateTextDocumentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    minio=Depends(get_minio_service),
):
    try:
        return create_text_document(
            db=db,
            minio=minio,
            project_id=project_id,
            phase_id=phase_id,
            session_id=session_id,
            filename=payload.filename,
            content=payload.content,
            current_user=current_user,
        )
    except ResourceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.post(
    "/projects/{project_id}/phases/{phase_id}/sessions/{session_id}/documents/upload",
    response_model=UploadedDocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    project_id: str,
    phase_id: str,
    session_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    minio=Depends(get_minio_service),
):
    try:
        content = await file.read()
        return upload_document_file(
            db=db,
            minio=minio,
            project_id=project_id,
            phase_id=phase_id,
            session_id=session_id,
            filename=file.filename or "uploaded_file",
            payload=content,
            content_type=file.content_type,
            current_user=current_user,
        )
    except ResourceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.get(
    "/projects/{project_id}/phases/{phase_id}/sessions/{session_id}/documents/{filename}/versions",
    response_model=FileVersionsResponse,
)
def list_document_versions(
    project_id: str,
    phase_id: str,
    session_id: str,
    filename: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    minio=Depends(get_minio_service),
):
    try:
        return get_document_versions(
            db=db,
            minio=minio,
            project_id=project_id,
            phase_id=phase_id,
            session_id=session_id,
            filename=filename,
            current_user=current_user,
        )
    except ResourceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.get(
    "/projects/{project_id}/phases/{phase_id}/sessions/{session_id}/documents/{filename}/versions/{version_id}/content",
    response_model=FileContentResponse,
)
def get_document_content(
    project_id: str,
    phase_id: str,
    session_id: str,
    filename: str,
    version_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    minio=Depends(get_minio_service),
):
    try:
        return get_document_content_by_version(
            db=db,
            minio=minio,
            project_id=project_id,
            phase_id=phase_id,
            session_id=session_id,
            filename=filename,
            version_id=version_id,
            current_user=current_user,
        )
    except ResourceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.get("/projects/{project_id}/documents/tree", response_model=ProjectDocumentTreeResponse)
def get_project_documents_tree(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    minio=Depends(get_minio_service),
):
    try:
        return get_project_document_tree(db=db, minio=minio, project_id=project_id, current_user=current_user)
    except ResourceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.get("/projects/{project_id}/phases/{phase_id}/documents", response_model=PhaseDocumentsResponse)
def get_phase_documents_route(
    project_id: str,
    phase_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    minio=Depends(get_minio_service),
):
    try:
        return get_phase_documents(db=db, minio=minio, project_id=project_id, phase_id=phase_id, current_user=current_user)
    except ResourceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.get(
    "/projects/{project_id}/phases/{phase_id}/sessions/{session_id}/documents",
    response_model=SessionDocumentsResponse,
)
def get_session_documents_route(
    project_id: str,
    phase_id: str,
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    minio=Depends(get_minio_service),
):
    try:
        return get_session_documents(
            db=db,
            minio=minio,
            project_id=project_id,
            phase_id=phase_id,
            session_id=session_id,
            current_user=current_user,
        )
    except ResourceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.get(
    "/projects/{project_id}/phases/{phase_id}/sessions/{session_id}/versions",
    response_model=SessionVersionHistoryResponse,
)
def get_session_versions_route(
    project_id: str,
    phase_id: str,
    session_id: str,
    previous_only: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return get_session_version_history(
            db=db,
            project_id=project_id,
            phase_id=phase_id,
            session_id=session_id,
            current_user=current_user,
            previous_only=previous_only,
        )
    except ResourceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

@router.post(
    "/projects/{project_id}/phases/{phase_id}/sessions/{session_id}/versions",
    response_model=SessionVersionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_session_version(
    project_id: str,
    phase_id: str,
    session_id: str,
    payload: SessionVersionCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return create_new_session_version(
            db=db,
            project_id=project_id,
            phase_id=phase_id,
            session_id=session_id,
            remark=payload.remark,
            current_user=current_user,
        )
    except ResourceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc



@router.get("/projects/{project_id}/phases/sessions/status", response_model=ProjectWorkflowStatusResponse)
def get_phase_session_status(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return get_project_phase_session_status(db=db, project_id=project_id, current_user=current_user)
    except ResourceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc


@router.post("/projects/{project_id}/phases/{phase_id}/approve", response_model=PhaseStatusResponse)
def approve_phase_route(
    project_id: str,
    phase_id: str,
    payload: RemarkRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return approve_phase(
            db=db,
            project_id=project_id,
            phase_id=phase_id,
            remark=payload.remark,
            current_user=current_user,
        )
    except ResourceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc


@router.post(
    "/projects/{project_id}/phases/{phase_id}/sessions/{session_id}/versions/{version}/approve",
    response_model=SessionVersionResponse,
)
def approve_session_route(
    project_id: str,
    phase_id: str,
    session_id: str,
    version: int,
    payload: RemarkRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return approve_session_version(
            db=db,
            project_id=project_id,
            phase_id=phase_id,
            session_id=session_id,
            version=version,
            remark=payload.remark,
            current_user=current_user,
        )
    except ResourceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc


@router.patch(
    "/projects/{project_id}/phases/{phase_id}/sessions/{session_id}/name",
    response_model=SessionVersionResponse,
)
def rename_session_route(
    project_id: str,
    phase_id: str,
    session_id: str,
    payload: SessionRenameRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return rename_session_title(
            db=db,
            project_id=project_id,
            phase_id=phase_id,
            session_id=session_id,
            session_title=payload.session_title,
            current_user=current_user,
        )
    except ResourceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
