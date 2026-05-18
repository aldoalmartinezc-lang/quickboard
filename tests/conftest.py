"""Pytest configuration and shared fixtures for QuickBoard tests."""

import pytest

from quickboard.main import create_app


@pytest.fixture
def app_factory():
    """Return a factory that creates a QuickBoard app backed by a temp SQLite DB."""

    def _factory(tmp_path, *, database_url=None):
        url = database_url or f"sqlite:///{tmp_path / 'qb.db'}"
        return create_app(url)

    return _factory