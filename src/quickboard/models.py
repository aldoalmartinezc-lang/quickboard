"""Persistent domain models for QuickBoard.

Entities: Board, List, Card, Tag, CardTag.

Key design decisions (see ADR-001):
- Explicit integer `position` field on List and Card for stable ordering.
- completed_at marks done cards (NULL = pending).
- Tag names are unique; CardTag is the many-to-many join table.
- All timestamps are UTC.
"""

from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


def _utcnow() -> datetime:
    return datetime.now(UTC)


# ---------------------------------------------------------------------------
# Board
# ---------------------------------------------------------------------------

class Board(SQLModel, table=True):
    __tablename__ = "board"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    position: int = Field(default=0, index=True)
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime | None = Field(default=None)


# ---------------------------------------------------------------------------
# List  (ordered within a Board)
# ---------------------------------------------------------------------------

class List(SQLModel, table=True):
    __tablename__ = "list"

    id: int | None = Field(default=None, primary_key=True)
    board_id: int = Field(foreign_key="board.id", index=True)
    name: str = Field(index=True)
    position: int = Field(default=0, index=True)
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime | None = Field(default=None)


# ---------------------------------------------------------------------------
# Card  (ordered within a List)
# ---------------------------------------------------------------------------

class Card(SQLModel, table=True):
    __tablename__ = "card"

    id: int | None = Field(default=None, primary_key=True)
    list_id: int = Field(foreign_key="list.id", index=True)
    title: str = Field(index=True)
    description: str = Field(default="")
    position: int = Field(default=0, index=True)
    completed_at: datetime | None = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime | None = Field(default=None)


# ---------------------------------------------------------------------------
# Tag  (unique label)
# ---------------------------------------------------------------------------

class Tag(SQLModel, table=True):
    __tablename__ = "tag"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)


# ---------------------------------------------------------------------------
# CardTag  (many-to-many join)
# ---------------------------------------------------------------------------

class CardTag(SQLModel, table=True):
    __tablename__ = "card_tag"

    card_id: int = Field(foreign_key="card.id", primary_key=True)
    tag_id: int = Field(foreign_key="tag.id", primary_key=True)