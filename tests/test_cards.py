import pytest
from httpx import ASGITransport, AsyncClient

from quickboard.main import create_app


@pytest.mark.asyncio
async def test_card_lifecycle_and_tags(tmp_path):
    app = create_app(f"sqlite:///{tmp_path / 'qb.db'}")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        board = (await client.post("/boards", json={"name": "Work"})).json()
        todo = (await client.post(f"/boards/{board['id']}/lists", json={"name": "Todo"})).json()
        doing = (await client.post(f"/boards/{board['id']}/lists", json={"name": "Doing"})).json()

        card = (await client.post(
            f"/lists/{todo['id']}/cards",
            json={"title": "Ship MVP", "description": "core", "tags": ["api", "mvp"]},
        )).json()
        assert card["position"] == 0
        assert card["tags"] == ["api", "mvp"]

        moved = (await client.post(
            f"/cards/{card['id']}/move",
            json={"list_id": doing['id'], "position": 0},
        )).json()
        assert moved["list_id"] == doing["id"]
        assert moved["position"] == 0

        completed = (await client.post(f"/cards/{card['id']}/complete")).json()
        assert completed["completed_at"] is not None

        retagged = (await client.put(f"/cards/{card['id']}/tags", json={"tags": ["blocked", "urgent"]})).json()
        assert retagged["tags"] == ["blocked", "urgent"]

        cards = (await client.get(f"/lists/{doing['id']}/cards")).json()
        assert len(cards) == 1
        assert cards[0]["title"] == "Ship MVP"

        await client.delete(f"/cards/{card['id']}")
        assert (await client.get(f"/lists/{doing['id']}/cards")).json() == []


@pytest.mark.asyncio
async def test_card_search_and_reordering(tmp_path):
    app = create_app(f"sqlite:///{tmp_path / 'qb.db'}")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        board = (await client.post("/boards", json={"name": "Search"})).json()
        todo = (await client.post(f"/boards/{board['id']}/lists", json={"name": "Todo"})).json()
        await client.post(f"/lists/{todo['id']}/cards", json={"title": "Write docs", "description": "finish README"})
        await client.post(f"/lists/{todo['id']}/cards", json={"title": "Refactor", "description": "keep searchable"})
        search = (await client.get("/cards/search", params={"q": "README"})).json()
        assert [card["title"] for card in search] == ["Write docs"]
        search = (await client.get("/cards/search", params={"q": "search"})).json()
        assert [card["title"] for card in search] == ["Refactor"]


@pytest.mark.asyncio
async def test_card_reordering_within_and_across_lists(tmp_path):
    app = create_app(f"sqlite:///{tmp_path / 'qb.db'}")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        board = (await client.post("/boards", json={"name": "Order"})).json()
        source = (await client.post(f"/boards/{board['id']}/lists", json={"name": "Source"})).json()
        target = (await client.post(f"/boards/{board['id']}/lists", json={"name": "Target"})).json()
        a = (await client.post(f"/lists/{source['id']}/cards", json={"title": "A"})).json()
        b = (await client.post(f"/lists/{source['id']}/cards", json={"title": "B"})).json()
        x = (await client.post(f"/lists/{target['id']}/cards", json={"title": "X"})).json()

        await client.post(f"/cards/{a['id']}/move", json={"list_id": source['id'], "position": 1})
        source_cards = (await client.get(f"/lists/{source['id']}/cards")).json()
        assert [card["title"] for card in source_cards] == ["B", "A"]

        await client.post(f"/cards/{b['id']}/move", json={"list_id": target['id'], "position": 0})
        target_cards = (await client.get(f"/lists/{target['id']}/cards")).json()
        assert [card["title"] for card in target_cards] == ["B", "X"]
        assert target_cards[0]["position"] == 0
        assert target_cards[1]["position"] == 1