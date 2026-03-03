from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from services.api.sessions.model import ProjectPhaseState, ProjectSessionVersion


def get_phase_state(db: Session, project_id: str, phase_id: str) -> ProjectPhaseState | None:
    stmt = select(ProjectPhaseState).where(ProjectPhaseState.project_id == project_id, ProjectPhaseState.phase_id == phase_id)
    return db.execute(stmt).scalar_one_or_none()


def save_phase_state(db: Session, state: ProjectPhaseState) -> ProjectPhaseState:
    db.add(state)
    db.commit()
    db.refresh(state)
    return state


def get_session_version(
    db: Session,
    project_id: str,
    phase_id: str,
    session_id: str,
    version: int,
) -> ProjectSessionVersion | None:
    stmt = select(ProjectSessionVersion).where(
        ProjectSessionVersion.project_id == project_id,
        ProjectSessionVersion.phase_id == phase_id,
        ProjectSessionVersion.session_id == session_id,
        ProjectSessionVersion.version == version,
    )
    return db.execute(stmt).scalar_one_or_none()


def get_next_session_version_number(db: Session, project_id: str, phase_id: str, session_id: str) -> int:
    stmt = select(func.max(ProjectSessionVersion.version)).where(
        ProjectSessionVersion.project_id == project_id,
        ProjectSessionVersion.phase_id == phase_id,
        ProjectSessionVersion.session_id == session_id,
    )
    latest_version = db.execute(stmt).scalar_one_or_none() or 0
    return int(latest_version) + 1


def save_session_version(db: Session, row: ProjectSessionVersion) -> ProjectSessionVersion:
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def list_phase_states(db: Session, project_id: str) -> list[ProjectPhaseState]:
    stmt = select(ProjectPhaseState).where(ProjectPhaseState.project_id == project_id)
    return list(db.execute(stmt).scalars().all())


def list_session_versions(db: Session, project_id: str) -> list[ProjectSessionVersion]:
    stmt = select(ProjectSessionVersion).where(ProjectSessionVersion.project_id == project_id)
    return list(db.execute(stmt).scalars().all())


def list_session_versions_for_session(
    db: Session,
    project_id: str,
    phase_id: str,
    session_id: str,
) -> list[ProjectSessionVersion]:
    stmt = (
        select(ProjectSessionVersion)
        .where(
            ProjectSessionVersion.project_id == project_id,
            ProjectSessionVersion.phase_id == phase_id,
            ProjectSessionVersion.session_id == session_id,
        )
        .order_by(desc(ProjectSessionVersion.version))
    )
    return list(db.execute(stmt).scalars().all())
