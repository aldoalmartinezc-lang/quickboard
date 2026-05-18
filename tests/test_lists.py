"""Tests for List CRUD endpoints: create, list, get, rename, delete, move."""

import pytest
from httpx import ASGITransport, AsyncClient

from quickboard.main import create_app

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _create_board(client: AsyncClient, name: str = "TestBoard") -> dict:
    return (await client.post("/boards", json={"name": name})).json()


async def _create_list(client: AsyncClient, board_id: int, name: str = "Todo") -> dict:
    return (await client.post(f"/boards/{board_id}/lists", json={"name": name})).json()


# ---------------------------------------------------------------------------
# POST /boards/{board_id}/lists — create list
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_list(tmp_path):
    app = create_app(f"sqlite:///{tmp_path / 'qb.db'}")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        board = await _create_board(client)
        lst = (await client.post(f"/boards/{board['id']}/lists", json={"name": "Todo"})).json()
        assert lst["name"] == "Todo"
        assert lst["board_id"] == board["id"]
        assert lst["position"] == 0


@pytest.mark.asyncio
async def test_create_list_strips_whitespace(tmp_path):
    app = create_app(f"sqlite:///{tmp_path / 'qb.db'}")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        board = await _create_board(client)
        lst = (await client.post(f"/boards/{board['id']}/lists", json={"name": "  Doing  "})).json()
        assert lst["name"] == "Doing"


@pytest.mark.asyncio
async def test_create_list_auto_positions(tmp_path):
    app = create_app(f"sqlite:///{tmp_path / 'qb.db'}")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        board = await _create_board(client)
        todo_list = await _create_list(client, board["id"], "Todo")
        doing_list = await _create_list(client, board["id"], "Doing")
        done_list = await _create_list(client, board["id"], "Done")
        assert todo_list["position"] == 0
        assert doing_list["position"] == 1
        assert done_list["position"] == 2


@pytest.mark.asyncio
async def test_create_list_board_not_found(tmp_path):
    app = create_app(f"sqlite:///{tmp_path / 'qb.db'}")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/boards/9999/lists", json={"name": "X"})
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# GET /boards/{board_id}/lists — list lists
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_lists_empty(tmp_path):
    app = create_app(f"sqlite:///{tmp_path / 'qb.db'}")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        board = await _create_board(client)
        lists = (await client.get(f"/boards/{board['id']}/lists")).json()
        assert lists == []


@pytest.mark.asyncio
async def test_list_lists_returns_all_in_order(tmp_path):
    app = create_app(f"sqlite:///{tmp_path / 'qb.db'}")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        board = await _create_board(client)
        await _create_list(client, board["id"], "Todo")
        await _create_list(client, board["id"], "Doing")
        lists = (await client.get(f"/boards/{board['id']}/lists")).json()
        assert len(lists) == 2
        assert [item["name"] for item in lists] == ["Todo", "Doing"]


@pytest.mark.asyncio
async def test_list_lists_board_not_found(tmp_path):
    app = create_app(f"sqlite:///{tmp_path / 'qb.db'}")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/boards/9999/lists")
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# GET /lists/{list_id} — get list detail (with cards)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_list_detail(tmp_path):
    app = create_app(f"sqlite:///{tmp_path / 'qb.db'}")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        board = await _create_board(client)
        lst = await _create_list(client, board["id"], "Todo")
        detail = (await client.get(f"/lists/{lst['id']}")).json()
        assert detail["name"] == "Todo"
        assert detail["board_id"] == board["id"]
        assert "cards" in detail


@pytest.mark.asyncio
async def test_get_list_detail_includes_cards(tmp_path):
    app = create_app(f"sqlite:///{tmp_path / 'qb.db'}")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        board = await _create_board(client)
        lst = await _create_list(client, board["id"], "Todo")
        await client.post(f"/lists/{lst['id']}/cards", json={"title": "Task 1"})
        await client.post(f"/lists/{lst['id']}/cards", json={"title": "Task 2"})
        detail = (await client.get(f"/lists/{lst['id']}")).json()
        assert len(detail["cards"]) == 2
        assert detail["cards"][0]["title"] == "Task 1"


@pytest.mark.asyncio
async def test_get_list_not_found(tmp_path):
    app = create_app(f"sqlite:///{tmp_path / 'qb.db'}")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/lists/9999")
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# PATCH /lists/{list_id} — rename list
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_rename_list(tmp_path):
    app = create_app(f"sqlite:///{tmp_path / 'qb.db'}")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        board = await _create_board(client)
        lst = await _create_list(client, board["id"], "Todo")
        renamed = (await client.patch(f"/lists/{lst['id']}", json={"name": "In Progress"})).json()
        assert renamed["name"] == "In Progress"
        assert renamed["id"] == lst["id"]
        assert renamed["updated_at"] is not None


@pytest.mark.asyncio
async def test_rename_list_strips_whitespace(tmp_path):
    app = create_app(f"sqlite:///{tmp_path / 'qb.db'}")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        board = await _create_board(client)
        lst = await _create_list(client, board["id"], "A")
        renamed = (await client.patch(f"/lists/{lst['id']}", json={"name": " B "})).json()
        assert renamed["name"] == "B"


@pytest.mark.asyncio
async def test_rename_list_not_found(tmp_path):
    app = create_app(f"sqlite:///{tmp_path / 'qb.db'}")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.patch("/lists/9999", json={"name": "X"})
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /lists/{list_id} — delete list
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_delete_list(tmp_path):
    app = create_app(f"sqlite:///{tmp_path / 'qb.db'}")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        board = await _create_board(client)
        lst = await _create_list(client, board["id"], "Todo")
        response = await client.delete(f"/lists/{lst['id']}")
        assert response.status_code == 204
        lists = (await client.get(f"/boards/{board['id']}/lists")).json()
        assert lists == []


@pytest.mark.asyncio
async def test_delete_list_not_found(tmp_path):
    app = create_app(f"sqlite:///{tmp_path / 'qb.db'}")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.delete("/lists/9999")
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_list_reindexes_remaining(tmp_path):
    """After deleting a list, remaining lists should have contiguous positions."""
    app = create_app(f"sqlite:///{tmp_path / 'qb.db'}")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        board = await _create_board(client)
        todo_list = await _create_list(client, board["id"], "Todo")
        doing_list = await _create_list(client, board["id"], "Doing")
        done_list = await _create_list(client, board["id"], "Done")
        await client.delete(f"/lists/{doing_list['id']}")
        lists = (await client.get(f"/boards/{board['id']}/lists")).json()
        assert len(lists) == 2
        assert [item["name"] for item in lists] == ["Todo", "Done"]
        assert [item["position"] for item in lists] == [0, 1]
        assert todo_list["id"] != done_list["id"]


@pytest.mark.asyncio
async def test_delete_list_cascades_cards(tmp_path):
    """Deleting a list should also remove all its cards."""
    app = create_app(f"sqlite:///{tmp_path / 'qb.db'}")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        board = await _create_board(client)
        lst = await _create_list(client, board["id"], "Todo")
        await client.post(f"/lists/{lst['id']}/cards", json={"title": "Task"})
        await client.delete(f"/lists/{lst['id']}")
        detail = (await client.get(f"/boards/{board['id']}")).json()
        assert detail["lists"] == []


# ---------------------------------------------------------------------------
# POST /lists/{list_id}/move — reorder list
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_move_list_to_position(tmp_path):
    app = create_app(f"sqlite:///{tmp_path / 'qb.db'}")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        board = await _create_board(client)
        todo_list = await _create_list(client, board["id"], "Todo")
        await _create_list(client, board["id"], "Doing")
        await _create_list(client, board["id"], "Done")
        moved = (await client.post(f"/lists/{todo_list['id']}/move", json={"position": 2})).json()
        assert moved["position"] == 2
        lists = (await client.get(f"/boards/{board['id']}/lists")).json()
        assert [item["name"] for item in lists] == ["Doing", "Done", "Todo"]


@pytest.mark.asyncio
async def test_move_list_to_front(tmp_path):
    app = create_app(f"sqlite:///{tmp_path / 'qb.db'}")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        board = await _create_board(client)
        await _create_list(client, board["id"], "Todo")
        await _create_list(client, board["id"], "Doing")
        done_list = await _create_list(client, board["id"], "Done")
        moved = (await client.post(f"/lists/{done_list['id']}/move", json={"position": 0})).json()
        assert moved["position"] == 0
        lists = (await client.get(f"/boards/{board['id']}/lists")).json()
        assert [item["name"] for item in lists] == ["Done", "Todo", "Doing"]


@pytest.mark.asyncio
async def test_move_list_clamps_overflow(tmp_path):
    """Position beyond range should clamp to end."""
    app = create_app(f"sqlite:///{tmp_path / 'qb.db'}")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        board = await _create_board(client)
        todo_list = await _create_list(client, board["id"], "Todo")
        await _create_list(client, board["id"], "Doing")
        moved = (await client.post(f"/lists/{todo_list['id']}/move", json={"position": 99})).json()
        assert moved["position"] == 1
        lists = (await client.get(f"/boards/{board['id']}/lists")).json()
        assert [item["name"] for item in lists] == ["Doing", "Todo"]


@pytest.mark.asyncio
async def test_move_list_not_found(tmp_path):
    app = create_app(f"sqlite:///{tmp_path / 'qb.db'}")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/lists/9999/move", json={"position": 0})
        assert response.status_code == 404
