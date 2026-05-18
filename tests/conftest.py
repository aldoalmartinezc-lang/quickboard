import pytest
from httpx import ASGITransport, AsyncClient

from quickboard.main import create_app


@pytest.fixture()
def app(tmp_path):
    db_path = tmp_path / "quickboard.db"
    return create_app(f"sqlite:///{db_path}")


@pytest.fixture()
def transport(app):
    return ASGITransport(app=app)


@pytest.fixture()
async def client(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as async_client:
        yield async_client
