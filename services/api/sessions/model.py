from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from services.core.database import Base


class ProjectPhaseState(Base):
    __tablename__ = "project_phase_states"
    __table_args__ = (UniqueConstraint("project_id", "phase_id", name="uq_project_phase"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    phase_id: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    approval_status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    approved_by_user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    project: Mapped["Project"] = relationship("Project")
    approved_by: Mapped["User"] = relationship("User", foreign_keys=[approved_by_user_id])


class ProjectSessionVersion(Base):
    __tablename__ = "project_session_versions"
    __table_args__ = (UniqueConstraint("project_id", "phase_id", "session_id", "version", name="uq_project_phase_session_version"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    phase_id: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    session_id: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    session_title: Mapped[str] = mapped_column(String(240), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    conversation_id: Mapped[str] = mapped_column(String(36), nullable=False, default=lambda: str(uuid4()))
    approval_status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    approved_by_user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_by_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)

    project: Mapped["Project"] = relationship("Project")
    approved_by: Mapped["User"] = relationship("User", foreign_keys=[approved_by_user_id])
    created_by: Mapped["User"] = relationship("User", foreign_keys=[created_by_user_id])


class ConversationState(Base):
    __tablename__ = "conversation_states"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    conversation_id: Mapped[str] = mapped_column(String(36), nullable=False, unique=True, index=True)
    first_message_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("conversation_messages.id", ondelete="SET NULL"),
        nullable=True,
    )
    last_message_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("conversation_messages.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )


class ConversationMessage(Base):
    __tablename__ = "conversation_messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    conversation_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    previous_message_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("conversation_messages.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    next_message_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("conversation_messages.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
