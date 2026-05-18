"""Tests for the persistence layer: model creation, schema init, and basic CRUD."""

from datetime import UTC

import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from quickboard.db import create_test_engine, init_db
from quickboard.models import Board, Card, CardTag, List, Tag


@pytest.fixture
def session():
    """Provide a fresh in-memory SQLite session for each test."""
    engine = create_test_engine()
    init_db(engine)
    with Session(engine) as session:
        yield session


# ---------------------------------------------------------------------------
# Schema creation
# ---------------------------------------------------------------------------

class TestSchemaInit:
    def test_init_db_creates_all_tables(self):
        engine = create_test_engine()
        init_db(engine)
        # All five tables should exist
        from sqlmodel import SQLModel
        expected = {"board", "list", "card", "tag", "card_tag"}
        actual = set(SQLModel.metadata.tables.keys())
        assert expected <= actual

    def test_init_db_idempotent(self):
        """Running init_db twice must not raise."""
        engine = create_test_engine()
        init_db(engine)
        init_db(engine)  # second call is safe


# ---------------------------------------------------------------------------
# Board
# ---------------------------------------------------------------------------

class TestBoard:
    def test_create_board(self, session):
        board = Board(name="Personal", position=0)
        session.add(board)
        session.commit()
        session.refresh(board)
        assert board.id is not None
        assert board.name == "Personal"
        assert board.position == 0
        assert board.created_at is not None

    def test_board_default_position(self, session):
        board = Board(name="Work")
        session.add(board)
        session.commit()
        session.refresh(board)
        assert board.position == 0

    def test_board_ordering(self, session):
        b0 = Board(name="First", position=0)
        b1 = Board(name="Second", position=1)
        session.add(b0)
        session.add(b1)
        session.commit()
        boards = session.exec(select(Board).order_by(Board.position)).all()
        assert [b.name for b in boards] == ["First", "Second"]


# ---------------------------------------------------------------------------
# List
# ---------------------------------------------------------------------------

class TestList:
    def test_create_list_in_board(self, session):
        board = Board(name="Board", position=0)
        session.add(board)
        session.commit()
        lst = List(board_id=board.id, name="Todo", position=0)
        session.add(lst)
        session.commit()
        session.refresh(lst)
        assert lst.id is not None
        assert lst.board_id == board.id
        assert lst.name == "Todo"

    def test_list_ordering_within_board(self, session):
        board = Board(name="Board", position=0)
        session.add(board)
        session.commit()
        for i, name in enumerate(["Todo", "Doing", "Done"]):
            session.add(List(board_id=board.id, name=name, position=i))
        session.commit()
        lists = session.exec(
            select(List).where(List.board_id == board.id).order_by(List.position)
        ).all()
        assert [lst.name for lst in lists] == ["Todo", "Doing", "Done"]


# ---------------------------------------------------------------------------
# Card
# ---------------------------------------------------------------------------

class TestCard:
    def test_create_card_in_list(self, session):
        board = Board(name="B", position=0)
        session.add(board)
        session.commit()
        lst = List(board_id=board.id, name="L", position=0)
        session.add(lst)
        session.commit()
        card = Card(list_id=lst.id, title="Write tests", position=0)
        session.add(card)
        session.commit()
        session.refresh(card)
        assert card.id is not None
        assert card.title == "Write tests"
        assert card.description == ""
        assert card.completed_at is None

    def test_card_ordering_within_list(self, session):
        board = Board(name="B", position=0)
        session.add(board)
        session.commit()
        lst = List(board_id=board.id, name="L", position=0)
        session.add(lst)
        session.commit()
        for i, title in enumerate(["A", "B", "C"]):
            session.add(Card(list_id=lst.id, title=title, position=i))
        session.commit()
        cards = session.exec(
            select(Card).where(Card.list_id == lst.id).order_by(Card.position)
        ).all()
        assert [c.title for c in cards] == ["A", "B", "C"]

    def test_card_complete_sets_timestamp(self, session):
        from datetime import datetime
        board = Board(name="B", position=0)
        session.add(board)
        session.commit()
        lst = List(board_id=board.id, name="L", position=0)
        session.add(lst)
        session.commit()
        now = datetime.now(UTC)
        card = Card(list_id=lst.id, title="Done task", position=0, completed_at=now)
        session.add(card)
        session.commit()
        session.refresh(card)
        assert card.completed_at is not None


# ---------------------------------------------------------------------------
# Tag + CardTag
# ---------------------------------------------------------------------------

class TestTag:
    def test_create_tag(self, session):
        tag = Tag(name="urgent")
        session.add(tag)
        session.commit()
        session.refresh(tag)
        assert tag.id is not None
        assert tag.name == "urgent"

    def test_tag_name_unique(self, session):
        session.add(Tag(name="bug"))
        session.commit()
        session.add(Tag(name="bug"))
        with pytest.raises(IntegrityError):
            session.commit()

    def test_card_tag_association(self, session):
        board = Board(name="B", position=0)
        session.add(board)
        session.commit()
        lst = List(board_id=board.id, name="L", position=0)
        session.add(lst)
        session.commit()
        card = Card(list_id=lst.id, title="T", position=0)
        session.add(card)
        tag = Tag(name="feature")
        session.add(tag)
        session.commit()
        session.refresh(card)
        session.refresh(tag)
        ct = CardTag(card_id=card.id, tag_id=tag.id)
        session.add(ct)
        session.commit()
        # Verify the link
        links = session.exec(select(CardTag)).all()
        assert len(links) == 1
        assert links[0].card_id == card.id
        assert links[0].tag_id == tag.id