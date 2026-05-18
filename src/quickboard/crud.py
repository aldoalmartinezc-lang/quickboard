from __future__ import annotations

from collections.abc import Iterable
from datetime import UTC, datetime

from sqlalchemy import func
from sqlmodel import Session, select

from .models import Board, Card, CardTag, List, Tag


def utcnow() -> datetime:
    return datetime.now(UTC)


def _scalar_one(session: Session, statement) -> object:
    return session.exec(statement).one()


def board_by_id(session: Session, board_id: int) -> Board:
    board = session.get(Board, board_id)
    if board is None:
        raise KeyError(f"Board {board_id} not found")
    return board


def list_by_id(session: Session, list_id: int) -> List:
    list_obj = session.get(List, list_id)
    if list_obj is None:
        raise KeyError(f"List {list_id} not found")
    return list_obj


def card_by_id(session: Session, card_id: int) -> Card:
    card = session.get(Card, card_id)
    if card is None:
        raise KeyError(f"Card {card_id} not found")
    return card


def ordered_boards(session: Session) -> list[Board]:
    return list(session.exec(select(Board).order_by(Board.position, Board.id)).all())


def ordered_lists(session: Session, board_id: int) -> list[List]:
    statement = select(List).where(List.board_id == board_id).order_by(List.position, List.id)
    return list(session.exec(statement).all())


def ordered_cards(session: Session, list_id: int) -> list[Card]:
    statement = select(Card).where(Card.list_id == list_id).order_by(Card.position, Card.id)
    return list(session.exec(statement).all())


def tags_for_card(session: Session, card_id: int) -> list[str]:
    statement = (
        select(Tag.name)
        .join(CardTag, CardTag.tag_id == Tag.id)
        .where(CardTag.card_id == card_id)
        .order_by(Tag.name)
    )
    return list(session.exec(statement).all())


def next_position(session: Session, model, column) -> int:
    statement = select(func.coalesce(func.max(column), -1))
    return int(session.exec(statement).one()) + 1


def reindex_boards(session: Session) -> None:
    for index, board in enumerate(ordered_boards(session)):
        board.position = index
        board.updated_at = utcnow()
        session.add(board)


def reindex_lists(session: Session, board_id: int) -> None:
    for index, list_obj in enumerate(ordered_lists(session, board_id)):
        list_obj.position = index
        list_obj.updated_at = utcnow()
        session.add(list_obj)


def reindex_cards(session: Session, list_id: int) -> None:
    for index, card in enumerate(ordered_cards(session, list_id)):
        card.position = index
        card.updated_at = utcnow()
        session.add(card)


def board_to_dict(session: Session, board: Board, include_lists: bool = True) -> dict:
    payload = {
        "id": board.id,
        "name": board.name,
        "position": board.position,
        "created_at": board.created_at,
        "updated_at": board.updated_at,
    }
    if include_lists:
        payload["lists"] = [list_to_dict(session, list_obj, include_cards=True) for list_obj in ordered_lists(session, board.id)]
    return payload


def list_to_dict(session: Session, list_obj: List, include_cards: bool = True) -> dict:
    payload = {
        "id": list_obj.id,
        "board_id": list_obj.board_id,
        "name": list_obj.name,
        "position": list_obj.position,
        "created_at": list_obj.created_at,
        "updated_at": list_obj.updated_at,
    }
    if include_cards:
        payload["cards"] = [card_to_dict(session, card) for card in ordered_cards(session, list_obj.id)]
    return payload


def card_to_dict(session: Session, card: Card) -> dict:
    return {
        "id": card.id,
        "list_id": card.list_id,
        "title": card.title,
        "description": card.description,
        "position": card.position,
        "completed_at": card.completed_at,
        "created_at": card.created_at,
        "updated_at": card.updated_at,
        "tags": tags_for_card(session, card.id),
    }


def ensure_tags(session: Session, names: Iterable[str]) -> list[Tag]:
    tags: list[Tag] = []
    for raw_name in names:
        name = raw_name.strip()
        if not name:
            continue
        tag = session.exec(select(Tag).where(Tag.name == name)).first()
        if tag is None:
            tag = Tag(name=name)
            session.add(tag)
            session.flush()
        tags.append(tag)
    return tags


def replace_card_tags(session: Session, card_id: int, names: Iterable[str]) -> list[str]:
    existing = list(session.exec(select(CardTag).where(CardTag.card_id == card_id)).all())
    for relation in existing:
        session.delete(relation)
    unique_names = []
    seen: set[str] = set()
    for raw_name in names:
        name = raw_name.strip()
        if not name or name in seen:
            continue
        seen.add(name)
        unique_names.append(name)
    tag_rows = ensure_tags(session, unique_names)
    for tag in tag_rows:
        session.add(CardTag(card_id=card_id, tag_id=tag.id))
    return [tag.name for tag in tag_rows]
