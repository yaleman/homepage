"""tests for homepage app"""

from fastapi.testclient import TestClient
from homepage import app


def test_homepage() -> None:
    """tests homepage"""
    client = TestClient(app)

    assert client.get("/", headers={"host": "localhost:8000"})
    assert client.get("/", headers={"host": "example.com:8000"})


def test_config() -> None:
    """tests something"""
    client = TestClient(app)

    assert client.get("/config", headers={"host": "localhost:8000"})
    assert client.get("/config", headers={"host": "example.com:8000"})
