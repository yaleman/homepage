"""tests for homepage app"""

from typing import Any
from fastapi.testclient import TestClient
from homepage import get_app
from starlette.routing import Mount, Route

from homepage.config import ConfigFile


def test_homepage(monkeypatch: Any) -> None:
    """tests homepage"""

    monkeypatch.setenv("HOMEPAGE_CONFIG_FILE", "links.test.json")
    client = TestClient(get_app())
    assert client.get("/", headers={"host": "localhost:8000"})
    assert client.get("/", headers={"host": "example.com:8000"})


def test_all_routes(monkeypatch: Any) -> None:
    """tests all the routes"""
    monkeypatch.setenv("HOMEPAGE_CONFIG_FILE", "links.test.json")

    app = get_app()
    client = TestClient(app)

    config = ConfigFile.load_config()

    # validate that the config refuses to return a result if it's not a "local" host
    assert client.get("/config", headers={"host": "foo"}).status_code == 401
    assert (
        client.get("/config", headers={"host": config.hosts.internal[0]}).status_code
        == 200
    )

    for route in app.routes:
        if isinstance(route, Mount):
            print("Skipping route mount")
            continue
        elif isinstance(route, Route):
            if route.methods is None:
                raise Exception(f"No methods defined for route {route}")
            else:
                methods = route.methods
            for method in methods:
                assert client.request(
                    method, route.path, headers={"host": "localhost:8000"}
                )
        else:
            raise Exception(f"Unknown route type: {route}")
