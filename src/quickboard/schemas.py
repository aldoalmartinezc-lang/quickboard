from datetime import datetime

from sqlmodel import Field, SQLModel


class BoardCreate(SQLModel):
    name: str


class BoardUpdate(SQLModel):
    name: str


class ListCreate(SQLModel):
    name: str


class ListUpdate(SQLModel):
    name: str


class ListMove(SQLModel):
    position: int


class CardCreate(SQLModel):
    title: str
    description: str = ""
    tags: list[str] = Field(default_factory=list)


class CardUpdate(SQLModel):
    title: str | None = None
    description: str | None = None


class CardMove(SQLModel):
    list_id: int
    position: int | None = None


class CardTagsUpdate(SQLModel):
    tags: list[str] = Field(default_factory=list)


class BoardRead(SQLModel):
    id: int
    name: str
    position: int
    created_at: datetime
    updated_at: datetime | None = None


class ListRead(SQLModel):
    id: int
    board_id: int
    name: str
    position: int
    created_at: datetime
    updated_at: datetime | None = None


class CardRead(SQLModel):
    id: int
    list_id: int
    title: str
    description: str
    position: int
    completed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime | None = None
    tags: list[str] = Field(default_factory=list)


class ListDetail(ListRead):
    cards: list[CardRead] = Field(default_factory=list)


class BoardDetail(BoardRead):
    lists: list[ListDetail] = Field(default_factory=list)