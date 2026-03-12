"""Shared pytest fixtures for the fastapi-client test suite."""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Return a synchronous TestClient wrapping the FastAPI app."""
    return TestClient(app)
