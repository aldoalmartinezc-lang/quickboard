from __future__ import annotations

from datetime import datetime, timezone

from sqlmodel import Session, select

from . import crud
from .models import Board, Card, CardTag, List


class NotFoundError(KeyError):
    pass


def _get_or_raise(getter, *args):
    try:
        return getter(*args)
    except KeyError as exc:
        raise NotFoundError(str(exc)) from exc


def _resequence_cards(session: Session, list_id: int, cards: list[Card]) -> None:
    for index, item in enumerate(cards):
        item.list_id = list_id
        item.position = index
        item.updated_at = crud.utcnow()
        session.add(item)


def list_boards(session: Session) -> list[dict]:
    return [crud.board_to_dict(session, board) for board in crud.ordered_boards(session)]


def create_board(session: Session, name: str) -> dict:
    board_name = name.strip()
    board = Board(name=board_name, position=len(crud.ordered_boards(session)))
    session.add(board)
    session.commit()
    session.refresh(board)
    return crud.board_to_dict(session, board)


def get_board(session: Session, board_id: int) -> dict:
    return crud.board_to_dict(session, _get_or_raise(crud.board_by_id, session, board_id))


def rename_board(session: Session, board_id: int, name: str) -> dict:
    board = _get_or_raise(crud.board_by_id, session, board_id)
    board.name = name.strip()
    board.updated_at = crud.utcnow()
    session.add(board)
    session.commit()
    session.refresh(board)
    return crud.board_to_dict(session, board)


def delete_board(session: Session, board_id: int) -> None:
    board = _get_or_raise(crud.board_by_id, session, board_id)
    for list_obj in crud.ordered_lists(session, board.id):
        for card in crud.ordered_cards(session, list_obj.id):
            for relation in list(session.exec(select(CardTag).where(CardTag.card_id == card.id)).all()):
                session.delete(relation)
            session.delete(card)
        session.delete(list_obj)
    session.delete(board)
    session.commit()
    crud.reindex_boards(session)
    session.commit()


def list_lists(session: Session, board_id: int) -> list[dict]:
    _get_or_raise(crud.board_by_id, session, board_id)
    return [crud.list_to_dict(session, list_obj) for list_obj in crud.ordered_lists(session, board_id)]


def create_list(session: Session, board_id: int, name: str) -> dict:
    _get_or_raise(crud.board_by_id, session, board_id)
    list_name = name.strip()
    list_obj = List(board_id=board_id, name=list_name, position=len(crud.ordered_lists(session, board_id)))
    session.add(list_obj)
    session.commit()
    session.refresh(list_obj)
    crud.reindex_lists(session, board_id)
    session.commit()
    return crud.list_to_dict(session, list_obj)


def list_cards(session: Session, list_id: int) -> list[dict]:
    _get_or_raise(crud.list_by_id, session, list_id)
    return [crud.card_to_dict(session, card) for card in crud.ordered_cards(session, list_id)]


def create_card(session: Session, list_id: int, title: str, description: str = "", tags: list[str] | None = None) -> dict:
    _get_or_raise(crud.list_by_id, session, list_id)
    card_title = title.strip()
    card = Card(
        list_id=list_id,
        title=card_title,
        description=description or "",
        position=len(crud.ordered_cards(session, list_id)),
    )
    session.add(card)
    session.flush()
    if tags is not None:
        crud.replace_card_tags(session, card.id, tags)
    session.commit()
    session.refresh(card)
    return crud.card_to_dict(session, card)


def move_card(session: Session, card_id: int, list_id: int, position: int | None = None) -> dict:
    card = _get_or_raise(crud.card_by_id, session, card_id)
    source_list_id = card.list_id
    _get_or_raise(crud.list_by_id, session, list_id)
    source_cards = crud.ordered_cards(session, source_list_id)
    target_cards = crud.ordered_cards(session, list_id)
    source_cards = [item for item in source_cards if item.id != card.id]
    if source_list_id == list_id:
        target_cards = [item for item in target_cards if item.id != card.id]
    insert_at = len(target_cards) if position is None else max(0, min(position, len(target_cards)))
    card.list_id = list_id
    target_cards.insert(insert_at, card)
    if source_list_id == list_id:
        _resequence_cards(session, list_id, target_cards)
    else:
        _resequence_cards(session, source_list_id, source_cards)
        _resequence_cards(session, list_id, target_cards)
    session.commit()
    session.refresh(card)
    return crud.card_to_dict(session, card)


def complete_card(session: Session, card_id: int) -> dict:
    card = _get_or_raise(crud.card_by_id, session, card_id)
    if card.completed_at is None:
        card.completed_at = datetime.now(timezone.utc)
        card.updated_at = crud.utcnow()
        session.add(card)
        session.commit()
        session.refresh(card)
    return crud.card_to_dict(session, card)


def delete_card(session: Session, card_id: int) -> None:
    card = _get_or_raise(crud.card_by_id, session, card_id)
    list_id = card.list_id
    for relation in list(session.exec(select(CardTag).where(CardTag.card_id == card.id)).all()):
        session.delete(relation)
    session.delete(card)
    session.commit()
    crud.reindex_cards(session, list_id)
    session.commit()


def replace_tags(session: Session, card_id: int, tags: list[str]) -> dict:
    card = _get_or_raise(crud.card_by_id, session, card_id)
    crud.replace_card_tags(session, card.id, tags)
    card.updated_at = crud.utcnow()
    session.add(card)
    session.commit()
    session.refresh(card)
    return crud.card_to_dict(session, card)


def search_cards(session: Session, q: str) -> list[dict]:
    pattern = f"%{q.strip()}%"
    statement = (
        select(Card)
        .where(Card.title.ilike(pattern) | Card.description.ilike(pattern))
        .order_by(Card.created_at.desc(), Card.id.desc())
    )
    return [crud.card_to_dict(session, card) for card in session.exec(statement).all()]
