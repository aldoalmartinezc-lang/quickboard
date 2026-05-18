import pytest
from httpx import ASGITransport, AsyncClient

from quickboard.main import create_app


@pytest.mark.asyncio
async def test_board_list_card_crud_move_complete_and_delete(tmp_path):
    app = create_app(f"sqlite:///{tmp_path / 'quickboard.db'}")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        board = (await client.post("/boards", json={"name": "Work"})).json()
        assert board["name"] == "Work"
        assert board["position"] == 0

        renamed = (await client.patch(f"/boards/{board['id']}", json={"name": "Focus"})).json()
        assert renamed["name"] == "Focus"

        list_todo = (await client.post(f"/boards/{board['id']}/lists", json={"name": "Todo"})).json()
        list_doing = (await client.post(f"/boards/{board['id']}/lists", json={"name": "Doing"})).json()
        assert list_todo["position"] == 0
        assert list_doing["position"] == 1

        card = (await client.post(f"/lists/{list_todo['id']}/cards", json={"title": "Ship MVP", "description": "core flow", "tags": ["mvp", "api"]})).json()
        assert card["position"] == 0
        assert card["tags"] == ["api", "mvp"]

        moved = (await client.post(f"/cards/{card['id']}/move", json={"list_id": list_doing['id'], "position": 0})).json()
        assert moved["list_id"] == list_doing["id"]
        assert moved["position"] == 0

        completed = (await client.post(f"/cards/{card['id']}/complete")).json()
        assert completed["completed_at"] is not None

        updated_tags = (await client.put(f"/cards/{card['id']}/tags", json={"tags": ["blocked", "urgent"]})).json()
        assert updated_tags["tags"] == ["blocked", "urgent"]

        cards_in_doing = (await client.get(f"/lists/{list_doing['id']}/cards")).json()
        assert len(cards_in_doing) == 1
        assert cards_in_doing[0]["id"] == card["id"]
        assert cards_in_doing[0]["position"] == 0

        await client.delete(f"/cards/{card['id']}")
        assert (await client.get(f"/lists/{list_doing['id']}/cards")).json() == []

        await client.delete(f"/boards/{board['id']}")
        assert (await client.get("/boards")).json() == []
