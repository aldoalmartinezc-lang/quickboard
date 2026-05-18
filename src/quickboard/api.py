from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from .db import get_session
from .settings import Settings
from .schemas import (
    BoardCreate,
    BoardDetail,
    BoardRead,
    BoardUpdate,
    CardCreate,
    CardMove,
    CardRead,
    CardTagsUpdate,
    CardUpdate,
    ListCreate,
    ListDetail,
    ListMove,
    ListRead,
    ListUpdate,
)
from .services import (
    NotFoundError,
    complete_card,
    create_board,
    create_card,
    create_list,
    delete_board,
    delete_card,
    delete_list,
    get_board,
    get_list,
    list_boards,
    list_cards,
    list_lists,
    move_card,
    move_list,
    rename_board,
    rename_list,
    replace_tags,
    search_cards,
    uncomplete_card,
    update_card,
)

router = APIRouter()

_settings: Settings | None = None


def _get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


# ---------------------------------------------------------------------------
# Consistent error helpers
# ---------------------------------------------------------------------------


def _not_found(error: KeyError | NotFoundError) -> HTTPException:
    return HTTPException(status_code=404, detail=str(error))


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------


@router.get("/health", response_model=dict)
def health() -> dict[str, str]:
    return {"status": "ok", "version": _get_settings().version}


# ---------------------------------------------------------------------------
# Board CRUD
# ---------------------------------------------------------------------------


@router.get("/boards", response_model=list[BoardRead])
def get_boards(session: Session = Depends(get_session)):
    return list_boards(session)


@router.post("/boards", status_code=201, response_model=BoardRead)
def post_board(payload: BoardCreate, session: Session = Depends(get_session)):
    return create_board(session, payload.name)


@router.get("/boards/{board_id}", response_model=BoardDetail)
def get_board_detail(board_id: int, session: Session = Depends(get_session)):
    try:
        return get_board(session, board_id)
    except NotFoundError as error:
        raise _not_found(error) from error


@router.patch("/boards/{board_id}", response_model=BoardRead)
def patch_board(board_id: int, payload: BoardUpdate, session: Session = Depends(get_session)):
    try:
        return rename_board(session, board_id, payload.name)
    except NotFoundError as error:
        raise _not_found(error) from error


@router.delete("/boards/{board_id}", status_code=204)
def remove_board(board_id: int, session: Session = Depends(get_session)):
    try:
        delete_board(session, board_id)
    except NotFoundError as error:
        raise _not_found(error) from error


# ---------------------------------------------------------------------------
# List nested under Board (create + list)
# ---------------------------------------------------------------------------


@router.get("/boards/{board_id}/lists", response_model=list[ListRead])
def get_board_lists(board_id: int, session: Session = Depends(get_session)):
    try:
        return list_lists(session, board_id)
    except NotFoundError as error:
        raise _not_found(error) from error


@router.post("/boards/{board_id}/lists", status_code=201, response_model=ListRead)
def post_board_list(board_id: int, payload: ListCreate, session: Session = Depends(get_session)):
    try:
        return create_list(session, board_id, payload.name)
    except NotFoundError as error:
        raise _not_found(error) from error


# ---------------------------------------------------------------------------
# List CRUD (direct access by list_id)
# ---------------------------------------------------------------------------


@router.get("/lists/{list_id}", response_model=ListDetail)
def get_list_detail(list_id: int, session: Session = Depends(get_session)):
    try:
        return get_list(session, list_id)
    except NotFoundError as error:
        raise _not_found(error) from error


@router.patch("/lists/{list_id}", response_model=ListRead)
def patch_list(list_id: int, payload: ListUpdate, session: Session = Depends(get_session)):
    try:
        return rename_list(session, list_id, payload.name)
    except NotFoundError as error:
        raise _not_found(error) from error


@router.delete("/lists/{list_id}", status_code=204)
def remove_list(list_id: int, session: Session = Depends(get_session)):
    try:
        delete_list(session, list_id)
    except NotFoundError as error:
        raise _not_found(error) from error


@router.post("/lists/{list_id}/move", response_model=ListRead)
def post_move_list(list_id: int, payload: ListMove, session: Session = Depends(get_session)):
    try:
        return move_list(session, list_id, payload.position)
    except NotFoundError as error:
        raise _not_found(error) from error


# ---------------------------------------------------------------------------
# Card CRUD
# ---------------------------------------------------------------------------


@router.get("/lists/{list_id}/cards", response_model=list[CardRead])
def get_list_cards(list_id: int, session: Session = Depends(get_session)):
    try:
        return list_cards(session, list_id)
    except NotFoundError as error:
        raise _not_found(error) from error


@router.post("/lists/{list_id}/cards", status_code=201, response_model=CardRead)
def post_list_card(list_id: int, payload: CardCreate, session: Session = Depends(get_session)):
    try:
        return create_card(session, list_id, payload.title, payload.description, payload.tags)
    except NotFoundError as error:
        raise _not_found(error) from error


@router.post("/cards/{card_id}/move", response_model=CardRead)
def post_move_card(card_id: int, payload: CardMove, session: Session = Depends(get_session)):
    try:
        return move_card(session, card_id, payload.list_id, payload.position)
    except NotFoundError as error:
        raise _not_found(error) from error


@router.post("/cards/{card_id}/complete", response_model=CardRead)
def post_complete_card(card_id: int, session: Session = Depends(get_session)):
    try:
        return complete_card(session, card_id)
    except NotFoundError as error:
        raise _not_found(error) from error


@router.post("/cards/{card_id}/uncomplete", response_model=CardRead)
def post_uncomplete_card(card_id: int, session: Session = Depends(get_session)):
    try:
        return uncomplete_card(session, card_id)
    except NotFoundError as error:
        raise _not_found(error) from error


@router.patch("/cards/{card_id}", response_model=CardRead)
def patch_card(card_id: int, payload: CardUpdate, session: Session = Depends(get_session)):
    try:
        return update_card(session, card_id, payload.title, payload.description)
    except NotFoundError as error:
        raise _not_found(error) from error


@router.delete("/cards/{card_id}", status_code=204)
def remove_card(card_id: int, session: Session = Depends(get_session)):
    try:
        delete_card(session, card_id)
    except NotFoundError as error:
        raise _not_found(error) from error


@router.put("/cards/{card_id}/tags", response_model=CardRead)
def put_card_tags(card_id: int, payload: CardTagsUpdate, session: Session = Depends(get_session)):
    try:
        return replace_tags(session, card_id, payload.tags)
    except NotFoundError as error:
        raise _not_found(error) from error


@router.get("/cards/search", response_model=list[CardRead])
def find_cards(q: str = Query(min_length=1), session: Session = Depends(get_session)):
    return search_cards(session, q)