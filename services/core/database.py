from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from services.core.config import settings


class Base(DeclarativeBase):
    pass


_connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True, connect_args=_connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    # Import models so SQLAlchemy metadata is fully populated before create_all.
    from services.api.projects import model as _project_models  # noqa: F401
    from services.api.users import model as _user_models  # noqa: F401

    Base.metadata.create_all(bind=engine)
