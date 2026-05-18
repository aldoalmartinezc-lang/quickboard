import pytest
from httpx import ASGITransport, AsyncClient

from quickboard.main import create_app


@pytest.mark.asyncio
async def test_health_reports_version_and_status(tmp_path):
    app = create_app(f"sqlite:///{tmp_path / 'quickboard.db'}")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "0.1.0"}