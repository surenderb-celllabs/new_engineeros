from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from services.api.projects.schema import (
    ProjectCreateRequest,
    ProjectResponse,
    ProjectUpdateRequest,
    ShareRequest,
    WorkspaceCreateRequest,
    WorkspaceResponse,
    WorkspaceUpdateRequest,
)
from services.api.projects.services import (
    create_workspace_for_user,
    create_workspace_project,
    edit_project,
    edit_workspace,
    get_project_details,
    get_user_workspaces,
    get_workspace_details,
    get_workspace_projects,
    remove_project,
    remove_workspace,
    share_project,
    share_workspace,
)
from services.api.users.model import User
from services.core.database import get_db
from services.core.exceptions import PermissionDeniedError, ResourceNotFoundError
from services.dependencies.auth import get_current_user


router = APIRouter(prefix="/users", tags=["projects"])


@router.post("/workspaces", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
def create_workspace(
    payload: WorkspaceCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return create_workspace_for_user(db, payload, current_user)


@router.get("/workspaces", response_model=list[WorkspaceResponse])
def list_workspaces(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_user_workspaces(db, current_user)


@router.get("/workspaces/{workspace_id}", response_model=WorkspaceResponse)
def get_workspace(workspace_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return get_workspace_details(db, workspace_id, current_user)
    except ResourceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc


@router.put("/workspaces/{workspace_id}", response_model=WorkspaceResponse)
def update_workspace(
    workspace_id: str,
    payload: WorkspaceUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return edit_workspace(db, workspace_id, payload, current_user)
    except ResourceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc


@router.delete("/workspaces/{workspace_id}")
def delete_workspace(workspace_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return remove_workspace(db, workspace_id, current_user)
    except ResourceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc


@router.post("/workspaces/{workspace_id}/share", response_model=WorkspaceResponse)
def share_workspace_route(
    workspace_id: str,
    payload: ShareRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return share_workspace(db, workspace_id, payload.email, current_user)
    except ResourceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc


@router.post("/workspaces/{workspace_id}/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project_in_workspace(
    workspace_id: str,
    payload: ProjectCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return create_workspace_project(db, workspace_id, payload, current_user)
    except ResourceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc


@router.get("/workspaces/{workspace_id}/projects", response_model=list[ProjectResponse])
def list_workspace_projects(workspace_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return get_workspace_projects(db, workspace_id, current_user)
    except ResourceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc


@router.get("/projects/{project_id}", response_model=ProjectResponse)
def get_project(project_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return get_project_details(db, project_id, current_user)
    except ResourceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc


@router.put("/projects/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: str,
    payload: ProjectUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return edit_project(db, project_id, payload, current_user)
    except ResourceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc


@router.delete("/projects/{project_id}")
def delete_project(project_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return remove_project(db, project_id, current_user)
    except ResourceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc


@router.post("/projects/{project_id}/share", response_model=ProjectResponse)
def share_project_route(
    project_id: str,
    payload: ShareRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return share_project(db, project_id, payload.email, current_user)
    except ResourceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
