"""QB-03: Card update, uncomplete, 404s, delete-reindex, tag edge cases."""

import pytest
from httpx import ASGITransport, AsyncClient

from quickboard.main import create_app


async def _board(client, name="Board"):
    return (await client.post("/boards", json={"name": name})).json()


async def _list(client, board_id, name="List"):
    return (await client.post(f"/boards/{board_id}/lists", json={"name": name})).json()


async def _card(client, list_id, title="Card", **kw):
    return (await client.post(f"/lists/{list_id}/cards", json={"title": title, **kw})).json()


@pytest.mark.asyncio
async def test_card_update_title_and_description(tmp_path):
    app = create_app(f"sqlite:///{tmp_path / 'qb.db'}")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        board = await _board(client)
        lst = await _list(client, board["id"])
        card = await _card(client, lst["id"], title="Old")
        # Update title only
        updated = (await client.patch(f"/cards/{card['id']}", json={"title": "New"})).json()
        assert updated["title"] == "New"
        assert updated["description"] == ""
        # Update description only
        updated = (await client.patch(f"/cards/{card['id']}", json={"description": "Updated desc"})).json()
        assert updated["description"] == "Updated desc"
        assert updated["title"] == "New"
        # Update both
        updated = (await client.patch(f"/cards/{card['id']}", json={"title": "Final", "description": "Both"})).json()
        assert updated["title"] == "Final"
        assert updated["description"] == "Both"
        # Strips whitespace
        updated = (await client.patch(f"/cards/{card['id']}", json={"title": "  padded  "})).json()
        assert updated["title"] == "padded"


@pytest.mark.asyncio
async def test_card_update_nonexistent_404(tmp_path):
    app = create_app(f"sqlite:///{tmp_path / 'qb.db'}")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.patch("/cards/9999", json={"title": "Nope"})
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_card_uncomplete(tmp_path):
    app = create_app(f"sqlite:///{tmp_path / 'qb.db'}")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        board = await _board(client)
        lst = await _list(client, board["id"])
        card = await _card(client, lst["id"], title="Task")
        assert card["completed_at"] is None
        # Complete
        completed = (await client.post(f"/cards/{card['id']}/complete")).json()
        assert completed["completed_at"] is not None
        # Uncomplete
        uncompleted = (await client.post(f"/cards/{card['id']}/uncomplete")).json()
        assert uncompleted["completed_at"] is None
        # Uncomplete again (idempotent)
        uncompleted2 = (await client.post(f"/cards/{card['id']}/uncomplete")).json()
        assert uncompleted2["completed_at"] is None
        # Complete again (idempotent)
        completed2 = (await client.post(f"/cards/{card['id']}/complete")).json()
        assert completed2["completed_at"] is not None


@pytest.mark.asyncio
async def test_card_uncomplete_nonexistent_404(tmp_path):
    app = create_app(f"sqlite:///{tmp_path / 'qb.db'}")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/cards/9999/uncomplete")
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_card_404_errors(tmp_path):
    """All card operations on nonexistent IDs return 404."""
    app = create_app(f"sqlite:///{tmp_path / 'qb.db'}")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        assert (await client.post("/lists/9999/cards", json={"title": "X"})).status_code == 404
        assert (await client.get("/lists/9999/cards")).status_code == 404
        assert (await client.post("/cards/9999/move", json={"list_id": 1, "position": 0})).status_code == 404
        assert (await client.post("/cards/9999/complete")).status_code == 404
        assert (await client.delete("/cards/9999")).status_code == 404
        assert (await client.put("/cards/9999/tags", json={"tags": ["x"]})).status_code == 404


@pytest.mark.asyncio
async def test_card_delete_reindexes_positions(tmp_path):
    """Deleting a card in the middle must leave remaining positions sequential."""
    app = create_app(f"sqlite:///{tmp_path / 'qb.db'}")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        board = await _board(client)
        lst = await _list(client, board["id"])
        await _card(client, lst["id"], title="A")
        c1 = await _card(client, lst["id"], title="B")
        await _card(client, lst["id"], title="C")
        # Delete middle card
        await client.delete(f"/cards/{c1['id']}")
        cards = (await client.get(f"/lists/{lst['id']}/cards")).json()
        assert [c["title"] for c in cards] == ["A", "C"]
        assert [c["position"] for c in cards] == [0, 1]


@pytest.mark.asyncio
async def test_tag_replace_and_remove(tmp_path):
    """Tags can be replaced and fully removed."""
    app = create_app(f"sqlite:///{tmp_path / 'qb.db'}")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        board = await _board(client)
        lst = await _list(client, board["id"])
        card = await _card(client, lst["id"], title="T", tags=["old"])
        assert card["tags"] == ["old"]
        # Replace tags
        updated = (await client.put(f"/cards/{card['id']}/tags", json={"tags": ["bug", "urgent"]})).json()
        assert sorted(updated["tags"]) == ["bug", "urgent"]
        # Remove all tags
        updated = (await client.put(f"/cards/{card['id']}/tags", json={"tags": []})).json()
        assert updated["tags"] == []


@pytest.mark.asyncio
async def test_tags_shared_across_cards(tmp_path):
    """The same tag name reused across cards should not create duplicates."""
    app = create_app(f"sqlite:///{tmp_path / 'qb.db'}")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        board = await _board(client)
        lst = await _list(client, board["id"])
        c0 = await _card(client, lst["id"], title="C1", tags=["shared"])
        c1 = await _card(client, lst["id"], title="C2", tags=["shared"])
        assert c0["tags"] == ["shared"]
        assert c1["tags"] == ["shared"]