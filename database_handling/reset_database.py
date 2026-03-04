#!/usr/bin/env python3
"""Reset application database by dropping and recreating all tables."""

from services.core.database import Base, engine

# Import all models so metadata is complete before drop/create.
from services.api.projects import model as _project_models  # noqa: F401
from services.api.sessions import model as _session_models  # noqa: F401
from services.api.users import model as _user_models  # noqa: F401


def reset_database() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    reset_database()
    print("Database reset complete: all tables dropped and recreated.")
