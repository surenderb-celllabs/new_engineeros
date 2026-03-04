from datetime import datetime

from pydantic import BaseModel, Field


class CreateTextDocumentRequest(BaseModel):
    filename: str = Field(..., min_length=1, max_length=255)
    content: str = Field(default="")


class UploadedDocumentResponse(BaseModel):
    filename: str
    object_key: str
    version_id: str | None
    download_url: str


class FileVersionResponse(BaseModel):
    version_id: str | None
    is_latest: bool
    last_modified: datetime | None
    size: int | None
    etag: str | None


class FileVersionsResponse(BaseModel):
    filename: str
    versions: list[FileVersionResponse]


class FileContentResponse(BaseModel):
    filename: str
    version_id: str | None
    content: str


class DocumentNode(BaseModel):
    filename: str
    object_key: str
    current_version: int | None
    current_version_id: str | None
    version_id: str | None
    last_modified: datetime | None
    download_url: str


class SessionDocumentsNode(BaseModel):
    session_id: str
    documents: list[DocumentNode]


class PhaseDocumentsNode(BaseModel):
    phase_id: str
    sessions: list[SessionDocumentsNode]


class ProjectDocumentTreeResponse(BaseModel):
    project_id: str
    phases: list[PhaseDocumentsNode]


class PhaseDocumentsResponse(BaseModel):
    project_id: str
    phase_id: str
    sessions: list[SessionDocumentsNode]


class SessionDocumentsResponse(BaseModel):
    project_id: str
    phase_id: str
    session_id: str
    documents: list[DocumentNode]


class RemarkRequest(BaseModel):
    remark: str | None = Field(default=None, max_length=2000)


class SessionVersionCreateRequest(BaseModel):
    remark: str | None = Field(default=None, max_length=2000)


class SessionRenameRequest(BaseModel):
    session_title: str = Field(..., min_length=1, max_length=240)


class SessionVersionResponse(BaseModel):
    id: str
    project_id: str
    phase_id: str
    session_id: str
    session_title: str
    version: int
    conversation_id: str
    approval_status: str
    remark: str | None
    output: str | None
    approved_at: datetime | None
    approved_by: str | None
    created_at: datetime
    updated_at: datetime


class SessionVersionHistoryResponse(BaseModel):
    project_id: str
    phase_id: str
    session_id: str
    versions: list[SessionVersionResponse]


class PhaseStatusResponse(BaseModel):
    phase_id: str
    phase_title: str
    approval_status: str
    remark: str | None
    approved_at: datetime | None
    approved_by: str | None
    documents_link: str


class SessionStatusResponse(BaseModel):
    session_id: str
    session_title: str
    latest_version: int | None
    approval_status: str
    remark: str | None
    approved_at: datetime | None
    approved_by: str | None
    documents_link: str


class PhaseWithSessionStatusResponse(BaseModel):
    phase: PhaseStatusResponse
    sessions: list[SessionStatusResponse]


class ProjectWorkflowStatusResponse(BaseModel):
    project_id: str
    phases: list[PhaseWithSessionStatusResponse]
