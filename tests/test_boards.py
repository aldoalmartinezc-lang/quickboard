import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
async def test_board_crud(app_factory, tmp_path):
    app = app_factory(tmp_path)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        created = (await client.post("/boards", json={"name": "Work"})).json()
        assert created["name"] == "Work"
        assert created["position"] == 0

        boards = (await client.get("/boards")).json()
        assert len(boards) == 1
        assert boards[0]["name"] == "Work"

        renamed = (await client.patch(f"/boards/{created['id']}", json={"name": "Focus"})).json()
        assert renamed["name"] == "Focus"

        detail = (await client.get(f"/boards/{created['id']}" )).json()
        assert detail["name"] == "Focus"
        assert detail["lists"] == []

        await client.delete(f"/boards/{created['id']}")
        assert (await client.get("/boards")).json() == []
