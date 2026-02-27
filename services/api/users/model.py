from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from services.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)

    owned_workspaces: Mapped[list["Workspace"]] = relationship(
        "Workspace",
        back_populates="owner",
        foreign_keys="Workspace.owner_id",
        cascade="all, delete-orphan",
    )
    workspace_memberships: Mapped[list["Workspace"]] = relationship(
        "Workspace",
        secondary="workspace_members",
        back_populates="members",
    )
    owned_projects: Mapped[list["Project"]] = relationship(
        "Project",
        back_populates="owner",
        foreign_keys="Project.owner_id",
        cascade="all, delete-orphan",
    )
    project_memberships: Mapped[list["Project"]] = relationship(
        "Project",
        secondary="project_members",
        back_populates="members",
    )


def build_user(email: str, full_name: str, hashed_password: str) -> User:
    return User(
        email=email,
        full_name=full_name,
        hashed_password=hashed_password,
    )
