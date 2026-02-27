from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from services.api.projects.model import Project, Workspace
from services.api.users.model import User


def create_workspace(db: Session, workspace: Workspace) -> Workspace:
    db.add(workspace)
    db.commit()
    db.refresh(workspace)
    return workspace


def get_workspace_by_id(db: Session, workspace_id: str) -> Workspace | None:
    stmt = (
        select(Workspace)
        .where(Workspace.id == workspace_id)
        .options(selectinload(Workspace.owner), selectinload(Workspace.members))
    )
    return db.execute(stmt).scalar_one_or_none()


def list_user_workspaces(db: Session, user: User) -> list[Workspace]:
    stmt = (
        select(Workspace)
        .outerjoin(Workspace.members)
        .where(or_(Workspace.owner_id == user.id, User.id == user.id))
        .distinct()
        .options(selectinload(Workspace.owner), selectinload(Workspace.members))
    )
    return list(db.execute(stmt).scalars().all())


def update_workspace(db: Session, workspace: Workspace, name: str | None, description: str | None) -> Workspace:
    if name is not None:
        workspace.name = name
    if description is not None:
        workspace.description = description
    db.commit()
    db.refresh(workspace)
    return workspace


def delete_workspace(db: Session, workspace: Workspace) -> None:
    db.delete(workspace)
    db.commit()


def add_workspace_member(db: Session, workspace: Workspace, user: User) -> Workspace:
    if all(member.id != user.id for member in workspace.members):
        workspace.members.append(user)
    db.commit()
    db.refresh(workspace)
    return workspace


def create_project(db: Session, project: Project) -> Project:
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def get_project_by_id(db: Session, project_id: str) -> Project | None:
    stmt = (
        select(Project)
        .where(Project.id == project_id)
        .options(
            selectinload(Project.owner),
            selectinload(Project.members),
            selectinload(Project.workspace).selectinload(Workspace.members),
            selectinload(Project.workspace).selectinload(Workspace.owner),
        )
    )
    return db.execute(stmt).scalar_one_or_none()


def list_projects_by_workspace(db: Session, workspace_id: str) -> list[Project]:
    stmt = (
        select(Project)
        .where(Project.workspace_id == workspace_id)
        .options(selectinload(Project.owner), selectinload(Project.members), selectinload(Project.workspace))
    )
    return list(db.execute(stmt).scalars().all())


def update_project(db: Session, project: Project, name: str | None, description: str | None) -> Project:
    if name is not None:
        project.name = name
    if description is not None:
        project.description = description
    db.commit()
    db.refresh(project)
    return project


def delete_project(db: Session, project: Project) -> None:
    db.delete(project)
    db.commit()


def add_project_member(db: Session, project: Project, user: User) -> Project:
    if all(member.id != user.id for member in project.members):
        project.members.append(user)
    db.commit()
    db.refresh(project)
    return project
