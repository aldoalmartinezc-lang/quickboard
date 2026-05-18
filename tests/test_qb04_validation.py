"""Tests for QB-04: schema validation, consistent error responses, and response_model typing."""

import pytest
from httpx import ASGITransport, AsyncClient

from quickboard.main import create_app


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _client(tmp_path):
    app = create_app(f"sqlite:///{tmp_path / 'qb.db'}")
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


async def _create_board(client: AsyncClient, name: str = "TestBoard") -> dict:
    return (await client.post("/boards", json={"name": name})).json()


async def _create_list(client: AsyncClient, board_id: int, name: str = "Todo") -> dict:
    return (await client.post(f"/boards/{board_id}/lists", json={"name": name})).json()


async def _create_card(client: AsyncClient, list_id: int, title: str = "Task") -> dict:
    return (await client.post(f"/lists/{list_id}/cards", json={"title": title})).json()


# ---------------------------------------------------------------------------
# Board validation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_board_empty_name(tmp_path):
    """POST /boards with empty name returns 422."""
    async with await _client(tmp_path) as client:
        resp = await client.post("/boards", json={"name": ""})
        assert resp.status_code == 422


@pytest.mark.asyncio
async def test_create_board_whitespace_only_name(tmp_path):
    """POST /boards with whitespace-only name returns 422 after strip."""
    async with await _client(tmp_path) as client:
        resp = await client.post("/boards", json={"name": "   "})
        assert resp.status_code == 422


@pytest.mark.asyncio
async def test_create_board_too_long_name(tmp_path):
    """POST /boards with name exceeding max length returns 422."""
    async with await _client(tmp_path) as client:
        resp = await client.post("/boards", json={"name": "x" * 121})
        assert resp.status_code == 422


@pytest.mark.asyncio
async def test_create_board_missing_name(tmp_path):
    """POST /boards with no name field returns 422."""
    async with await _client(tmp_path) as client:
        resp = await client.post("/boards", json={})
        assert resp.status_code == 422


@pytest.mark.asyncio
async def test_create_board_strips_whitespace(tmp_path):
    """POST /boards strips leading/trailing whitespace from name."""
    async with await _client(tmp_path) as client:
        board = (await client.post("/boards", json={"name": "  My Board  "}).json()
        assert board["name"] == "My Board"


@pytest.mark.asyncio
async def test_patch_board_empty_name(tmp_path):
    """PATCH /boards/{id} with empty name returns 422."""
    async with await _client(tmp_path) as client:
        board = await _create_board(client)
        resp = await client.patch(f"/boards/{board['id']}", json={"name": ""})
        assert resp.status_code == 422


@pytest.mark.asyncio
async def test_patch_board_too_long_name(tmp_path):
    """PATCH /boards/{id} with name exceeding max length returns 422."""
    async with await _client(tmp_path) as client:
        board = await _create_board(client)
        resp = await client.patch(f"/boards/{board['id']}", json={"name": "y" * 121})
        assert resp.status_code == 422


@pytest.mark.asyncio
async def test_board_not_found(tmp_path):
    """GET /boards/9999 returns 404 with structured error."""
    async with await _client(tmp_path) as client:
        resp = await client.get("/boards/9999")
        assert resp.status_code == 404
        body = resp.json()
        assert "detail" in body


@pytest.mark.asyncio
async def test_delete_board_not_found(tmp_path):
    """DELETE /boards/9999 returns 404."""
    async with await _client(tmp_path) as client:
        resp = await client.delete("/boards/9999")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# List validation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_list_empty_name(tmp_path):
    """POST /boards/{id}/lists with empty name returns 422."""
    async with await _client(tmp_path) as client:
        board = await _create_board(client)
        resp = await client.post(f"/boards/{board['id']}/lists", json={"name": ""})
        assert resp.status_code == 422


@pytest.mark.asyncio
async def test_create_list_too_long_name(tmp_path):
    """POST /boards/{id}/lists with name exceeding max length returns 422."""
    async with await _client(tmp_path) as client:
        board = await _create_board(client)
        resp = await client.post(f"/boards/{board['id']}/lists", json={"name": "z" * 121})
        assert resp.status_code == 422


@pytest.mark.asyncio
async def test_create_list_strips_whitespace(tmp_path):
    """POST /boards/{id}/lists strips leading/trailing whitespace."""
    async with await _client(tmp_path) as client:
        board = await _create_board(client)
        lst = (await client.post(f"/boards/{board['id']}/lists", json={"name": "  Doing  "})).json()
        assert lst["name"] == "Doing"


@pytest.mark.asyncio
async def test_list_not_found(tmp_path):
    """GET /lists/9999 returns 404."""
    async with await _client(tmp_path) as client:
        resp = await client.get("/lists/9999")
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_patch_list_empty_name(tmp_path):
    """PATCH /lists/{id} with empty name returns 422."""
    async with await _client(tmp_path) as client:
        board = await _create_board(client)
        lst = await _create_list(client, board["id"])
        resp = await client.patch(f"/lists/{lst['id']}", json={"name": ""})
        assert resp.status_code == 422


@pytest.mark.asyncio
async def test_move_list_negative_position(tmp_path):
    """POST /lists/{id}/move with negative position returns 422."""
    async with await _client(tmp_path) as client:
        board = await _create_board(client)
        lst = await _create_list(client, board["id"])
        resp = await client.post(f"/lists/{lst['id']}/move", json={"position": -1})
        assert resp.status_code == 422


@pytest.mark.asyncio
async def test_move_list_not_found(tmp_path):
    """POST /lists/9999/move returns 404."""
    async with await _client(tmp_path) as client:
        resp = await client.post("/lists/9999/move", json={"position": 0})
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Card validation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_card_empty_title(tmp_path):
    """POST /lists/{id}/cards with empty title returns 422."""
    async with await _client(tmp_path) as client:
        board = await _create_board(client)
        lst = await _create_list(client, board["id"])
        resp = await client.post(f"/lists/{lst['id']}/cards", json={"title": ""})
        assert resp.status_code == 422


@pytest.mark.asyncio
async def test_create_card_missing_title(tmp_path):
    """POST /lists/{id}/cards without title returns 422."""
    async with await _client(tmp_path) as client:
        board = await _create_board(client)
        lst = await _create_list(client, board["id"])
        resp = await client.post(f"/lists/{lst['id']}/cards", json={"description": "desc"})
        assert resp.status_code == 422


@pytest.mark.asyncio
async def test_create_card_too_long_title(tmp_path):
    """POST /lists/{id}/cards with title exceeding max length returns 422."""
    async with await _client(tmp_path) as client:
        board = await _create_board(client)
        lst = await _create_list(client, board["id"])
        resp = await client.post(f"/lists/{lst['id']}/cards", json={"title": "a" * 241})
        assert resp.status_code == 422


@pytest.mark.asyncio
async def test_create_card_too_long_description(tmp_path):
    """POST /lists/{id}/cards with description exceeding max length returns 422."""
    async with await _client(tmp_path) as client:
        board = await _create_board(client)
        lst = await _create_list(client, board["id"])
        resp = await client.post(f"/lists/{lst['id']}/cards", json={"title": "OK", "description": "d" * 2001})
        assert resp.status_code == 422


@pytest.mark.asyncio
async def test_create_card_too_many_tags(tmp_path):
    """POST /lists/{id}/cards with too many tags returns 422."""
    async with await _client(tmp_path) as client:
        board = await _create_board(client)
        lst = await _create_list(client, board["id"])
        resp = await client.post(
            f"/lists/{lst['id']}/cards",
            json={"title": "OK", "tags": [f"tag{i}" for i in range(21)]},
        )
        assert resp.status_code == 422


@pytest.mark.asyncio
async def test_create_card_tag_too_long(tmp_path):
    """POST /lists/{id}/cards with a tag exceeding max length returns 422."""
    async with await _client(tmp_path) as client:
        board = await _create_board(client)
        lst = await _create_list(client, board["id"])
        resp = await client.post(
            f"/lists/{lst['id']}/cards",
            json={"title": "OK", "tags": ["x" * 61]},
        )
        assert resp.status_code == 422


@pytest.mark.asyncio
async def test_create_card_empty_tag(tmp_path):
    """POST /lists/{id}/cards with an empty tag returns 422."""
    async with await _client(tmp_path) as client:
        board = await _create_board(client)
        lst = await _create_list(client, board["id"])
        resp = await client.post(
            f"/lists/{lst['id']}/cards",
            json={"title": "OK", "tags": [""]},
        )
        assert resp.status_code == 422


@pytest.mark.asyncio
async def test_create_card_strips_title_whitespace(tmp_path):
    """POST /lists/{id}/cards strips leading/trailing whitespace from title."""
    async with await _client(tmp_path) as client:
        board = await _create_board(client)
        lst = await _create_list(client, board["id"])
        card = (await client.post(f"/lists/{lst['id']}/cards", json={"title": "  Task  "})).json()
        assert card["title"] == "Task"


@pytest.mark.asyncio
async def test_create_card_strips_tag_whitespace(tmp_path):
    """POST /lists/{id}/cards strips whitespace from tags."""
    async with await _client(tmp_path) as client:
        board = await _create_board(client)
        lst = await _create_list(client, board["id"])
        card = (await client.post(
            f"/lists/{lst['id']}/cards",
            json={"title": "Task", "tags": ["  urgent  ", "  bug  "]},
        )).json()
        assert card["tags"] == ["urgent", "bug"]


@pytest.mark.asyncio
async def test_card_not_found(tmp_path):
    """GET /cards/9999 returns 404."""
    async with await _client(tmp_path) as client:
        resp = await client.get("/cards/9999")
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_patch_card_empty_title(tmp_path):
    """PATCH /cards/{id} with empty title returns 422."""
    async with await _client(tmp_path) as client:
        board = await _create_board(client)
        lst = await _create_list(client, board["id"])
        card = await _create_card(client, lst["id"])
        resp = await client.patch(f"/cards/{card['id']}", json={"title": ""})
        assert resp.status_code == 422


@pytest.mark.asyncio
async def test_move_card_invalid_list_id(tmp_path):
    """POST /cards/{id}/move with list_id <= 0 returns 422."""
    async with await _client(tmp_path) as client:
        board = await _create_board(client)
        lst = await _create_list(client, board["id"])
        card = await _create_card(client, lst["id"])
        resp = await client.post(f"/cards/{card['id']}/move", json={"list_id": 0, "position": 0})
        assert resp.status_code == 422


@pytest.mark.asyncio
async def test_move_card_negative_position(tmp_path):
    """POST /cards/{id}/move with negative position returns 422."""
    async with await _client(tmp_path) as client:
        board = await _create_board(client)
        lst = await _create_list(client, board["id"])
        card = await _create_card(client, lst["id"])
        resp = await client.post(f"/cards/{card['id']}/move", json={"list_id": lst["id"], "position": -1})
        assert resp.status_code == 422


@pytest.mark.asyncio
async def test_put_tags_empty_tag(tmp_path):
    """PUT /cards/{id}/tags with empty tag returns 422."""
    async with await _client(tmp_path) as client:
        board = await _create_board(client)
        lst = await _create_list(client, board["id"])
        card = await _create_card(client, lst["id"])
        resp = await client.put(f"/cards/{card['id']}/tags", json={"tags": [""]})
        assert resp.status_code == 422


@pytest.mark.asyncio
async def test_put_tags_too_many(tmp_path):
    """PUT /cards/{id}/tags with too many tags returns 422."""
    async with await _client(tmp_path) as client:
        board = await _create_board(client)
        lst = await _create_list(client, board["id"])
        card = await _create_card(client, lst["id"])
        resp = await client.put(f"/cards/{card['id']}/tags", json={"tags": [f"t{i}" for i in range(21)]})
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Consistent error format
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_validation_error_format(tmp_path):
    """422 validation errors have a consistent JSON structure."""
    async with await _client(tmp_path) as client:
        resp = await client.post("/boards", json={"name": ""})
        assert resp.status_code == 422
        body = resp.json()
        assert "detail" in body
        assert "errors" in body
        # Each error has field, message, type
        assert len(body["errors"]) > 0
        for err in body["errors"]:
            assert "field" in err
            assert "message" in err
            assert "type" in err


@pytest.mark.asyncio
async def test_404_error_has_detail(tmp_path):
    """404 errors return JSON with a detail key."""
    async with await _client(tmp_path) as client:
        resp = await client.get("/boards/9999")
        assert resp.status_code == 404
        body = resp.json()
        assert "detail" in body


# ---------------------------------------------------------------------------
# Search validation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_search_cards_empty_query(tmp_path):
    """GET /cards/search with empty q returns 422."""
    async with await _client(tmp_path) as client:
        resp = await client.get("/cards/search?q=")
        assert resp.status_code == 422


@pytest.mark.asyncio
async def test_search_cards_missing_query(tmp_path):
    """GET /cards/search without q parameter returns 422."""
    async with await _client(tmp_path) as client:
        resp = await client.get("/cards/search")
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Response model validation (field presence)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_board_response_has_expected_fields(tmp_path):
    """Board responses include id, name, position, created_at, updated_at."""
    async with await _client(tmp_path) as client:
        board = (await client.post("/boards", json={"name": "Check"})).json()
        assert "id" in board
        assert "name" in board
        assert "position" in board
        assert "created_at" in board
        assert "updated_at" in board


@pytest.mark.asyncio
async def test_board_detail_includes_lists(tmp_path):
    """Board detail response includes nested lists with cards."""
    async with await _client(tmp_path) as client:
        board = await _create_board(client)
        await _create_list(client, board["id"], "Todo")
        detail = (await client.get(f"/boards/{board['id']}")).json()
        assert "lists" in detail
        assert len(detail["lists"]) == 1
        assert "cards" in detail["lists"][0]


@pytest.mark.asyncio
async def test_list_detail_includes_cards(tmp_path):
    """List detail response includes cards."""
    async with await _client(tmp_path) as client:
        board = await _create_board(client)
        lst = await _create_list(client, board["id"])
        await _create_card(client, lst["id"], "Task 1")
        detail = (await client.get(f"/lists/{lst['id']}")).json()
        assert "cards" in detail
        assert len(detail["cards"]) == 1


@pytest.mark.asyncio
async def test_card_response_has_expected_fields(tmp_path):
    """Card responses include all expected fields."""
    async with await _client(tmp_path) as client:
        board = await _create_board(client)
        lst = await _create_list(client, board["id"])
        card = (await client.post(f"/lists/{lst['id']}/cards", json={
            "title": "My Task",
            "description": "A description",
            "tags": ["urgent", "bug"],
        })).json()
        for field in ("id", "list_id", "title", "description", "position", "completed_at", "created_at", "updated_at", "tags"):
            assert field in card, f"Missing field {field}"
        assert card["tags"] == ["urgent", "bug"]


@pytest.mark.asyncio
async def test_boards_list_returns_array(tmp_path):
    """GET /boards returns a list."""
    async with await _client(tmp_path) as client:
        resp = await client.get("/boards")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_delete_returns_204(tmp_path):
    """DELETE endpoints return 204 No Content on success."""
    async with await _client(tmp_path) as client:
        board = await _create_board(client)
        resp = await client.delete(f"/boards/{board['id']}")
        assert resp.status_code == 204