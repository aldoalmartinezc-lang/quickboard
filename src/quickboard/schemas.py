from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel


class BoardCreate(SQLModel):
    name: str


class BoardRead(BoardCreate):
    id: int
    position: int
    created_at: datetime


class BoardUpdate(SQLModel):
    name: Optional[str] = None


class ListCreate(SQLModel):
    name: str


class ListRead(ListCreate):
    id: int
    board_id: int
    position: int
    created_at: datetime


class ListUpdate(SQLModel):
    name: Optional[str] = None


class CardCreate(SQLModel):
    title: str
    description: str = ""
    tags: list[str] = []


class CardRead(CardCreate):
    id: int
    list_id: int
    position: int
    completed_at: Optional[datetime] = None
    created_at: datetime


class CardUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None


class CardMove(SQLModel):
    list_id: int
    position: Optional[int] = None


class TagRead(SQLModel):
    id: int
    name: str
