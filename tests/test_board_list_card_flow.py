import pytest
from httpx import ASGITransport, AsyncClient

from quickboard.main import create_app


@pytest.mark.asyncio
async def test_end_to_end_board_list_card_flow(tmp_path):
    app = create_app(f"sqlite:///{tmp_path / 'qb.db'}")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        board = (await client.post("/boards", json={"name": "MVP"})).json()
        todo = (await client.post(f"/boards/{board['id']}/lists", json={"name": "Todo"})).json()
        done = (await client.post(f"/boards/{board['id']}/lists", json={"name": "Done"})).json()
        card = (await client.post(f"/lists/{todo['id']}/cards", json={"title": "Start"})).json()
        await client.post(f"/cards/{card['id']}/move", json={"list_id": done['id'], "position": 0})
        await client.post(f"/cards/{card['id']}/complete")
        detail = (await client.get(f"/boards/{board['id']}")).json()
        assert [item["name"] for item in detail["lists"]] == ["Todo", "Done"]
        assert detail["lists"][1]["cards"][0]["completed_at"] is not None