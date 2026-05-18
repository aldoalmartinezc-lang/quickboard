import pytest
from httpx import ASGITransport, AsyncClient

from quickboard.main import create_app


@pytest.mark.asyncio
async def test_search_finds_cards_by_title_or_description(tmp_path):
    app = create_app(f"sqlite:///{tmp_path / 'quickboard.db'}")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        board = (await client.post("/boards", json={"name": "Search"})).json()
        todo = (await client.post(f"/boards/{board['id']}/lists", json={"name": "Todo"})).json()
        await client.post(f"/lists/{todo['id']}/cards", json={"title": "Write docs", "description": "finish README"})
        await client.post(f"/lists/{todo['id']}/cards", json={"title": "Refactor", "description": "keep searchable"})

        docs = (await client.get("/cards/search", params={"q": "README"})).json()
        assert [card["title"] for card in docs] == ["Write docs"]

        search = (await client.get("/cards/search", params={"q": "search"})).json()
        assert [card["title"] for card in search] == ["Refactor"]