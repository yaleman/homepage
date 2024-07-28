"""tests for homepage app"""

from typing import Any
from fastapi.testclient import TestClient
from homepage import get_app


def test_homepage(monkeypatch: Any) -> None:
    """tests homepage"""

    monkeypatch.setenv("HOMEPAGE_CONFIG_FILE", "links.test.json")
    client = TestClient(get_app())
    assert client.get("/", headers={"host": "localhost:8000"})
    assert client.get("/", headers={"host": "example.com:8000"})
