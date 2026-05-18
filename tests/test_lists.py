import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
async def test_list_crud_and_ordering(app_factory, tmp_path):
    app = app_factory(tmp_path)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        board = (await client.post("/boards", json={"name": "Work"})).json()
        first = (await client.post(f"/boards/{board['id']}/lists", json={"name": "Todo"})).json()
        second = (await client.post(f"/boards/{board['id']}/lists", json={"name": "Doing"})).json()

        assert first["position"] == 0
        assert second["position"] == 1

        board_detail = (await client.get(f"/boards/{board['id']}" )).json()
        assert [item["name"] for item in board_detail["lists"]] == ["Todo", "Doing"]

        lists = (await client.get(f"/boards/{board['id']}/lists")).json()
        assert [item["name"] for item in lists] == ["Todo", "Doing"]

        missing = await client.get("/boards/999/lists")
        assert missing.status_code == 404
