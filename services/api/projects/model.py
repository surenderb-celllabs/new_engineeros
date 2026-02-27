from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from services.core.database import Base


workspace_members = Table(
    "workspace_members",
    Base.metadata,
    Column("workspace_id", String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
)


project_members = Table(
    "project_members",
    Base.metadata,
    Column("project_id", String(36), ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
)


class Workspace(Base):
    __tablename__ = "workspaces"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)

    owner: Mapped["User"] = relationship("User", back_populates="owned_workspaces", foreign_keys=[owner_id])
    members: Mapped[list["User"]] = relationship("User", secondary=workspace_members, back_populates="workspace_memberships")
    projects: Mapped[list["Project"]] = relationship("Project", back_populates="workspace", cascade="all, delete-orphan")


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    workspace_id: Mapped[str] = mapped_column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)

    workspace: Mapped[Workspace] = relationship("Workspace", back_populates="projects")
    owner: Mapped["User"] = relationship("User", back_populates="owned_projects", foreign_keys=[owner_id])
    members: Mapped[list["User"]] = relationship("User", secondary=project_members, back_populates="project_memberships")


def build_workspace(name: str, description: str | None, owner_id: int) -> Workspace:
    return Workspace(name=name, description=description, owner_id=owner_id)


def build_project(workspace_id: str, name: str, description: str | None, owner_id: int) -> Project:
    return Project(workspace_id=workspace_id, name=name, description=description, owner_id=owner_id)
