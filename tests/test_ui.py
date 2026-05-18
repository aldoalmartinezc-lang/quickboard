import pytest
from httpx import ASGITransport, AsyncClient

from quickboard.main import create_app


@pytest.mark.asyncio
async def test_root_serves_minimal_ui(tmp_path):
    app = create_app(f"sqlite:///{tmp_path / 'quickboard.db'}")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/")
    assert response.status_code == 200
    assert "QuickBoard" in response.text
    assert "fetch('/boards')" in response.text
    assert "fetch('/health')" in response.text
