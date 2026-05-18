from datetime import datetime

from pydantic import field_validator
from sqlmodel import Field, SQLModel

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

NAME_MAX_LEN = 120
TITLE_MAX_LEN = 240
DESC_MAX_LEN = 2000
TAG_MAX_LEN = 60
TAG_MAX_COUNT = 20

# ---------------------------------------------------------------------------
# Request schemas (validated payloads)
# ---------------------------------------------------------------------------


class BoardCreate(SQLModel):
    name: str = Field(min_length=1, max_length=NAME_MAX_LEN)

    @field_validator("name")
    @classmethod
    def _strip_name(cls, v: str) -> str:
        return v.strip()


class BoardUpdate(SQLModel):
    name: str = Field(min_length=1, max_length=NAME_MAX_LEN)

    @field_validator("name")
    @classmethod
    def _strip_name(cls, v: str) -> str:
        return v.strip()


class ListCreate(SQLModel):
    name: str = Field(min_length=1, max_length=NAME_MAX_LEN)

    @field_validator("name")
    @classmethod
    def _strip_name(cls, v: str) -> str:
        return v.strip()


class ListUpdate(SQLModel):
    name: str = Field(min_length=1, max_length=NAME_MAX_LEN)

    @field_validator("name")
    @classmethod
    def _strip_name(cls, v: str) -> str:
        return v.strip()


class ListMove(SQLModel):
    position: int = Field(ge=0)


class CardCreate(SQLModel):
    title: str = Field(min_length=1, max_length=TITLE_MAX_LEN)
    description: str = Field(default="", max_length=DESC_MAX_LEN)
    tags: list[str] = Field(default_factory=list, max_length=TAG_MAX_COUNT)

    @field_validator("title")
    @classmethod
    def _strip_title(cls, v: str) -> str:
        return v.strip()

    @field_validator("tags")
    @classmethod
    def _validate_tags(cls, v: list[str]) -> list[str]:
        for tag in v:
            if len(tag) > TAG_MAX_LEN:
                raise ValueError(f"Tag too long (max {TAG_MAX_LEN} chars): {tag!r}")
            if not tag.strip():
                raise ValueError("Tags must not be empty")
        return [t.strip() for t in v]


class CardUpdate(SQLModel):
    title: str | None = Field(default=None, min_length=1, max_length=TITLE_MAX_LEN)
    description: str | None = Field(default=None, max_length=DESC_MAX_LEN)

    @field_validator("title")
    @classmethod
    def _strip_title(cls, v: str | None) -> str | None:
        return v.strip() if v is not None else None


class CardMove(SQLModel):
    list_id: int = Field(gt=0)
    position: int | None = Field(default=None, ge=0)


class CardTagsUpdate(SQLModel):
    tags: list[str] = Field(default_factory=list, max_length=TAG_MAX_COUNT)

    @field_validator("tags")
    @classmethod
    def _validate_tags(cls, v: list[str]) -> list[str]:
        for tag in v:
            if len(tag) > TAG_MAX_LEN:
                raise ValueError(f"Tag too long (max {TAG_MAX_LEN} chars): {tag!r}")
            if not tag.strip():
                raise ValueError("Tags must not be empty")
        return [t.strip() for t in v]


# ---------------------------------------------------------------------------
# Response schemas (typed output models)
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Error response schema
# ---------------------------------------------------------------------------


class ErrorResponse(SQLModel):
    detail: str