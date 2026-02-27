from sqlalchemy.orm import Session

from services.api.projects.crud import (
    add_project_member,
    add_workspace_member,
    create_project,
    create_workspace,
    delete_project,
    delete_workspace,
    get_project_by_id,
    get_workspace_by_id,
    list_projects_by_workspace,
    list_user_workspaces,
    update_project,
    update_workspace,
)
from services.api.projects.model import Project, Workspace, build_project, build_workspace
from services.api.projects.schema import (
    ProjectCreateRequest,
    ProjectResponse,
    ProjectUpdateRequest,
    WorkspaceCreateRequest,
    WorkspaceResponse,
    WorkspaceUpdateRequest,
)
from services.api.users.crud import get_user_by_email
from services.api.users.model import User
from services.core.exceptions import PermissionDeniedError, ResourceNotFoundError


def can_access_workspace(workspace: Workspace, current_user: User) -> bool:
    return workspace.owner_id == current_user.id or any(member.id == current_user.id for member in workspace.members)


def _can_access_project(project: Project, current_user: User) -> bool:
    return project.owner_id == current_user.id or any(member.id == current_user.id for member in project.members)


def _workspace_to_response(workspace: Workspace) -> WorkspaceResponse:
    members = sorted({member.email for member in workspace.members})
    return WorkspaceResponse(
        id=workspace.id,
        name=workspace.name,
        description=workspace.description,
        owner_email=workspace.owner.email,
        members=members,
        shared_with=members,
    )


def _project_to_response(project: Project) -> ProjectResponse:
    members = sorted({member.email for member in project.members})
    return ProjectResponse(
        id=project.id,
        workspace_id=project.workspace_id,
        name=project.name,
        description=project.description,
        owner_email=project.owner.email,
        members=members,
        shared_with=members,
    )


def create_workspace_for_user(db: Session, payload: WorkspaceCreateRequest, current_user: User) -> WorkspaceResponse:
    workspace = build_workspace(
        name=payload.name,
        description=payload.description,
        owner_id=current_user.id,
    )
    workspace.members.append(current_user)
    workspace = create_workspace(db, workspace)
    return _workspace_to_response(workspace)


def get_user_workspaces(db: Session, current_user: User) -> list[WorkspaceResponse]:
    workspaces = list_user_workspaces(db, current_user)
    return [_workspace_to_response(workspace) for workspace in workspaces]


def get_workspace_details(db: Session, workspace_id: str, current_user: User) -> WorkspaceResponse:
    workspace = get_workspace_by_id(db, workspace_id)
    if workspace is None:
        raise ResourceNotFoundError("Workspace not found")
    if not can_access_workspace(workspace, current_user):
        raise PermissionDeniedError("Access denied to workspace")
    return _workspace_to_response(workspace)


def edit_workspace(db: Session, workspace_id: str, payload: WorkspaceUpdateRequest, current_user: User) -> WorkspaceResponse:
    workspace = get_workspace_by_id(db, workspace_id)
    if workspace is None:
        raise ResourceNotFoundError("Workspace not found")
    if workspace.owner_id != current_user.id:
        raise PermissionDeniedError("Only workspace owner can edit workspace")

    updated = update_workspace(db, workspace, payload.name, payload.description)
    return _workspace_to_response(updated)


def remove_workspace(db: Session, workspace_id: str, current_user: User) -> dict[str, str]:
    workspace = get_workspace_by_id(db, workspace_id)
    if workspace is None:
        raise ResourceNotFoundError("Workspace not found")
    if workspace.owner_id != current_user.id:
        raise PermissionDeniedError("Only workspace owner can delete workspace")

    delete_workspace(db, workspace)
    return {"message": "Workspace deleted"}


def share_workspace(db: Session, workspace_id: str, collaborator_email: str, current_user: User) -> WorkspaceResponse:
    workspace = get_workspace_by_id(db, workspace_id)
    if workspace is None:
        raise ResourceNotFoundError("Workspace not found")
    if workspace.owner_id != current_user.id:
        raise PermissionDeniedError("Only workspace owner can share workspace")

    collaborator = get_user_by_email(db, collaborator_email)
    if collaborator is None:
        raise ResourceNotFoundError("Collaborator user not found")

    updated = add_workspace_member(db, workspace, collaborator)
    return _workspace_to_response(updated)


def create_workspace_project(
    db: Session,
    workspace_id: str,
    payload: ProjectCreateRequest,
    current_user: User,
) -> ProjectResponse:
    workspace = get_workspace_by_id(db, workspace_id)
    if workspace is None:
        raise ResourceNotFoundError("Workspace not found")
    if not can_access_workspace(workspace, current_user):
        raise PermissionDeniedError("Cannot create project in this workspace")

    project = build_project(
        workspace_id=workspace.id,
        name=payload.name,
        description=payload.description,
        owner_id=current_user.id,
    )
    project.members.append(current_user)
    project = create_project(db, project)
    return _project_to_response(project)


def get_workspace_projects(db: Session, workspace_id: str, current_user: User) -> list[ProjectResponse]:
    workspace = get_workspace_by_id(db, workspace_id)
    if workspace is None:
        raise ResourceNotFoundError("Workspace not found")
    if not can_access_workspace(workspace, current_user):
        raise PermissionDeniedError("Access denied to workspace projects")

    projects = list_projects_by_workspace(db, workspace_id)
    visible = [project for project in projects if can_access_workspace(workspace, current_user) or _can_access_project(project, current_user)]
    return [_project_to_response(project) for project in visible]


def get_project_details(db: Session, project_id: str, current_user: User) -> ProjectResponse:
    project = get_project_by_id(db, project_id)
    if project is None:
        raise ResourceNotFoundError("Project not found")
    if not (can_access_workspace(project.workspace, current_user) or _can_access_project(project, current_user)):
        raise PermissionDeniedError("Access denied to project")
    return _project_to_response(project)


def edit_project(db: Session, project_id: str, payload: ProjectUpdateRequest, current_user: User) -> ProjectResponse:
    project = get_project_by_id(db, project_id)
    if project is None:
        raise ResourceNotFoundError("Project not found")
    if project.owner_id != current_user.id:
        raise PermissionDeniedError("Only project owner can edit project")

    updated = update_project(db, project, payload.name, payload.description)
    return _project_to_response(updated)


def remove_project(db: Session, project_id: str, current_user: User) -> dict[str, str]:
    project = get_project_by_id(db, project_id)
    if project is None:
        raise ResourceNotFoundError("Project not found")
    if project.owner_id != current_user.id:
        raise PermissionDeniedError("Only project owner can delete project")

    delete_project(db, project)
    return {"message": "Project deleted"}


def share_project(db: Session, project_id: str, collaborator_email: str, current_user: User) -> ProjectResponse:
    project = get_project_by_id(db, project_id)
    if project is None:
        raise ResourceNotFoundError("Project not found")
    if project.owner_id != current_user.id:
        raise PermissionDeniedError("Only project owner can share project")

    collaborator = get_user_by_email(db, collaborator_email)
    if collaborator is None:
        raise ResourceNotFoundError("Collaborator user not found")

    updated = add_project_member(db, project, collaborator)
    return _project_to_response(updated)
