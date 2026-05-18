import pytest

from quickboard.main import create_app


@pytest.fixture()
def app_factory():
    def factory(tmp_path):
        return create_app(f"sqlite:///{tmp_path / 'quickboard.db'}")

    return factory
