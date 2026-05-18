"""Tests for QB-04: validation, error payloads, and response typing."""

import pytest
from httpx import ASGITransport, AsyncClient

from quickboard.main import create_app


def _app(tmp_path):
    return create_app(f"sqlite:///{tmp_path / 'qb.db'}")


async def _create_board(client: AsyncClient, name: str = "TestBoard") -> dict:
    return (await client.post("/boards", json={"name": name})).json()


async def _create_list(client: AsyncClient, board_id: int, name: str = "Todo") -> dict:
    return (await client.post(f"/boards/{board_id}/lists", json={"name": name})).json()


async def _create_card(
    client: AsyncClient,
    list_id: int,
    *,
    title: str = "Task",
    description: str | None = None,
    tags: list[str] | None = None,
) -> dict:
    payload: dict[str, object] = {"title": title}
    if description is not None:
        payload["description"] = description
    if tags is not None:
        payload["tags"] = tags
    return (await client.post(f"/lists/{list_id}/cards", json=payload)).json()


@pytest.mark.asyncio
async def test_create_board_validation(tmp_path):
    app = _app(tmp_path)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        assert (await client.post("/boards", json={"name": ""})).status_code == 422
        assert (await client.post("/boards", json={"name": "   "})).status_code == 422
        assert (await client.post("/boards", json={})).status_code == 422
        assert (await client.post("/boards", json={"name": "x" * 121})).status_code == 422


@pytest.mark.asyncio
async def test_create_board_strips_whitespace(tmp_path):
    app = _app(tmp_path)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        board = (await client.post("/boards", json={"name": "  My Board  "})).json()
        assert board["name"] == "My Board"


@pytest.mark.asyncio
async def test_board_not_found_returns_structured_404(tmp_path):
    app = _app(tmp_path)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/boards/9999")
        assert resp.status_code == 404
        body = resp.json()
        assert body["detail"].endswith("not found\'") or "not found" in body["detail"]


@pytest.mark.asyncio
async def test_delete_board_not_found_returns_404(tmp_path):
    app = _app(tmp_path)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        assert (await client.delete("/boards/9999")).status_code == 404


@pytest.mark.asyncio
async def test_create_list_validation(tmp_path):
    app = _app(tmp_path)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        board = await _create_board(client)
        assert (await client.post(f"/boards/{board['id']}/lists", json={"name": ""})).status_code == 422
        assert (await client.post(f"/boards/{board['id']}/lists", json={"name": "x" * 121})).status_code == 422


@pytest.mark.asyncio
async def test_create_list_strips_whitespace(tmp_path):
    app = _app(tmp_path)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        board = await _create_board(client)
        lst = await _create_list(client, board["id"], "  Doing  ")
        assert lst["name"] == "Doing"


@pytest.mark.asyncio
async def test_list_not_found_returns_404(tmp_path):
    app = _app(tmp_path)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/lists/9999")
        assert resp.status_code == 404
        assert resp.json()["detail"].endswith("not found\'") or "not found" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_move_list_validation(tmp_path):
    app = _app(tmp_path)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        board = await _create_board(client)
        lst = await _create_list(client, board["id"])
        assert (await client.post(f"/lists/{lst['id']}/move", json={"position": -1})).status_code == 422


@pytest.mark.asyncio
async def test_create_card_validation(tmp_path):
    app = _app(tmp_path)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        board = await _create_board(client)
        lst = await _create_list(client, board["id"])
        assert (await client.post(f"/lists/{lst['id']}/cards", json={"title": ""})).status_code == 422
        assert (await client.post(f"/lists/{lst['id']}/cards", json={"description": "desc"})).status_code == 422
        assert (await client.post(f"/lists/{lst['id']}/cards", json={"title": "x" * 241})).status_code == 422
        assert (await client.post(f"/lists/{lst['id']}/cards", json={"title": "OK", "description": "d" * 2001})).status_code == 422
        assert (
            await client.post(
                f"/lists/{lst['id']}/cards",
                json={"title": "OK", "tags": [f"tag{i}" for i in range(21)]},
            )
        ).status_code == 422
        assert (
            await client.post(f"/lists/{lst['id']}/cards", json={"title": "OK", "tags": ["x" * 65]} )
        ).status_code == 422


@pytest.mark.asyncio
async def test_create_card_response_has_expected_fields(tmp_path):
    app = _app(tmp_path)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        board = await _create_board(client)
        lst = await _create_list(client, board["id"])
        card = await _create_card(client, lst["id"], title="My Task", description="A description", tags=["urgent", "bug"])
        for field in ("id", "list_id", "title", "description", "position", "completed_at", "created_at", "updated_at", "tags"):
            assert field in card
        assert card["tags"] == ["bug", "urgent"]


@pytest.mark.asyncio
async def test_boards_list_returns_array(tmp_path):
    app = _app(tmp_path)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/boards")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_delete_returns_204(tmp_path):
    app = _app(tmp_path)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        board = await _create_board(client)
        resp = await client.delete(f"/boards/{board['id']}")
        assert resp.status_code == 204
