"""QB-05 acceptance tests: search, health, and minimal UI."""

import pytest
from httpx import ASGITransport, AsyncClient

from quickboard.main import create_app


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_health_returns_200_with_version_and_status(tmp_path):
    app = create_app(f"sqlite:///{tmp_path / 'qb.db'}")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "version" in body
    assert body["version"] == "0.1.0"


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_search_by_title(tmp_path):
    app = create_app(f"sqlite:///{tmp_path / 'qb.db'}")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        board = (await client.post("/boards", json={"name": "B1"})).json()
        todo = (await client.post(f"/boards/{board['id']}/lists", json={"name": "Todo"})).json()
        await client.post(f"/lists/{todo['id']}/cards", json={"title": "Fix login bug"})
        await client.post(f"/lists/{todo['id']}/cards", json={"title": "Write tests"})

        results = (await client.get("/cards/search", params={"q": "login"})).json()
        assert len(results) == 1
        assert results[0]["title"] == "Fix login bug"


@pytest.mark.asyncio
async def test_search_by_description(tmp_path):
    app = create_app(f"sqlite:///{tmp_path / 'qb.db'}")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        board = (await client.post("/boards", json={"name": "B1"})).json()
        todo = (await client.post(f"/boards/{board['id']}/lists", json={"name": "Todo"})).json()
        await client.post(f"/lists/{todo['id']}/cards", json={"title": "Task A", "description": "Deploy to production"})
        await client.post(f"/lists/{todo['id']}/cards", json={"title": "Task B", "description": "Refactor code"})

        results = (await client.get("/cards/search", params={"q": "prod"})).json()
        assert len(results) == 1
        assert results[0]["title"] == "Task A"


@pytest.mark.asyncio
async def test_search_case_insensitive(tmp_path):
    app = create_app(f"sqlite:///{tmp_path / 'qb.db'}")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        board = (await client.post("/boards", json={"name": "B1"})).json()
        todo = (await client.post(f"/boards/{board['id']}/lists", json={"name": "Todo"})).json()
        await client.post(f"/lists/{todo['id']}/cards", json={"title": "UPPERCASE ITEM"})

        results = (await client.get("/cards/search", params={"q": "uppercase"})).json()
        assert len(results) == 1


@pytest.mark.asyncio
async def test_search_no_results(tmp_path):
    app = create_app(f"sqlite:///{tmp_path / 'qb.db'}")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await client.post("/boards", json={"name": "B1"})
        results = (await client.get("/cards/search", params={"q": "nonexistent"})).json()
        assert results == []


@pytest.mark.asyncio
async def test_search_empty_query_returns_422(tmp_path):
    app = create_app(f"sqlite:///{tmp_path / 'qb.db'}")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/cards/search", params={"q": ""})
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_search_returns_card_with_tags(tmp_path):
    app = create_app(f"sqlite:///{tmp_path / 'qb.db'}")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        board = (await client.post("/boards", json={"name": "B1"})).json()
        todo = (await client.post(f"/boards/{board['id']}/lists", json={"name": "Todo"})).json()
        card = (
            await client.post(
                f"/lists/{todo['id']}/cards",
                json={"title": "Searchable", "description": "desc", "tags": ["urgent", "bug"]},
            )
        ).json()

        results = (await client.get("/cards/search", params={"q": "Searchable"})).json()
        assert len(results) == 1
        assert "tags" in results[0]
        assert results[0]["tags"] == ["bug", "urgent"]  # sorted alphabetically


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_ui_no_external_dependencies(tmp_path):
    """Verify the UI HTML has no links to external CSS/JS libraries."""
    app = create_app(f"sqlite:///{tmp_path / 'qb.db'}")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/")
    html = response.text.lower()
    # No CDN links, no external <link> or <script src="http">
    assert "cdn" not in html
    assert "unpkg" not in html
    assert "jsdelivr" not in html
    assert "cloudflare" not in html


@pytest.mark.asyncio
async def test_ui_calls_health_and_search(tmp_path):
    """Verify the UI JS code references /health and /cards/search."""
    app = create_app(f"sqlite:///{tmp_path / 'qb.db'}")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        html = (await client.get("/")).text
    assert "/health" in html
    assert "/cards/search" in html