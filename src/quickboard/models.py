from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


class Board(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    position: int = Field(default=0, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class List(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    board_id: int = Field(foreign_key="board.id", index=True)
    name: str = Field(index=True)
    position: int = Field(default=0, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Card(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    list_id: int = Field(foreign_key="list.id", index=True)
    title: str = Field(index=True)
    description: str = Field(default="")
    position: int = Field(default=0, index=True)
    completed_at: Optional[datetime] = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Tag(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)


class CardTag(SQLModel, table=True):
    card_id: int = Field(foreign_key="card.id", primary_key=True)
    tag_id: int = Field(foreign_key="tag.id", primary_key=True)
