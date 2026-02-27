from pydantic import BaseModel, EmailStr, Field


class ShareRequest(BaseModel):
    email: EmailStr


class WorkspaceCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=500)


class WorkspaceUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=500)


class WorkspaceResponse(BaseModel):
    id: str
    name: str
    description: str | None
    owner_email: EmailStr
    members: list[EmailStr]
    shared_with: list[EmailStr]


class ProjectCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=500)


class ProjectUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=500)


class ProjectResponse(BaseModel):
    id: str
    workspace_id: str
    name: str
    description: str | None
    owner_email: EmailStr
    members: list[EmailStr]
    shared_with: list[EmailStr]
