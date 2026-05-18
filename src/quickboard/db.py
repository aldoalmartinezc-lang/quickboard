"""Database engine, initialization, and session management.

- `init_db()` creates all tables if they don't exist yet.
- `get_session()` yields a Session for use as a FastAPI dependency.
- `create_test_engine()` returns an in-memory SQLite engine for tests.

The production engine is created eagerly at import time so that any
module that imports this file has access to `engine`.
"""

from collections.abc import Iterator

from sqlmodel import Session, SQLModel, create_engine

from . import models  # noqa: F401 - register tables before create_all
from .settings import Settings

settings = Settings()

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
    echo=False,
)


def init_db(eng=None) -> None:
    """Create all tables that don't exist yet.

    Accepts an optional engine argument so test suites can pass an
    in-memory engine without touching the production database.
    """
    target = eng or engine
    SQLModel.metadata.create_all(target)


def get_session() -> Iterator[Session]:
    """Yield a database session; intended as a FastAPI Depends()."""
    with Session(engine) as session:
        yield session


def create_test_engine():
    """Return a fresh in-memory SQLite engine for use in test fixtures."""
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        echo=False,
    )