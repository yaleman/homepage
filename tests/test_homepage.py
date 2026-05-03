"""tests for homepage app"""

import os
import socket
import subprocess
import sys
import time
from typing import Any, Iterator

from fastapi.testclient import TestClient
from homepage import get_app
from playwright.sync_api import Page, expect
import pytest
import requests
from starlette.routing import Mount, Route

from homepage.config import ConfigFile


@pytest.fixture
def live_homepage_server(monkeypatch: pytest.MonkeyPatch) -> Iterator[str]:
    """Run a live homepage server for browser tests."""
    monkeypatch.setenv("HOMEPAGE_CONFIG_FILE", "links.test.json")

    with socket.socket() as server_socket:
        server_socket.bind(("127.0.0.1", 0))
        port = server_socket.getsockname()[1]

    env = os.environ.copy()
    env["HOMEPAGE_CONFIG_FILE"] = "links.test.json"

    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "homepage:get_app",
            "--factory",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    base_url = f"http://127.0.0.1:{port}"

    try:
        for _ in range(50):
            try:
                response = requests.get(f"{base_url}/health", timeout=0.2)
                if response.ok:
                    break
            except requests.RequestException:
                time.sleep(0.1)
        else:
            raise RuntimeError("Timed out waiting for homepage test server")

        yield base_url
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


def test_homepage(monkeypatch: Any) -> None:
    """tests homepage"""

    monkeypatch.setenv("HOMEPAGE_CONFIG_FILE", "links.test.json")
    client = TestClient(get_app())
    response = client.get("/", headers={"host": "localhost:8000"})
    assert response
    assert 'href="/static/css/homepage.css"' in response.text
    assert "/static/css/bootstrap.min.css" not in response.text
    assert "/static/js/bootstrap.min.js" not in response.text
    assert '/static/js/homepage.js" defer' in response.text
    config = ConfigFile.load_config()
    for link in config.get_links(host="localhost:8000"):
        assert f'id="link-{link.id}"' in response.text
        assert f'data-title="{link.title}"' in response.text
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


def test_search_filters_link_cards(
    page: Page, live_homepage_server: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Search filters link cards by data-title in a real browser."""
    monkeypatch.setenv("HOMEPAGE_CONFIG_FILE", "links.test.json")
    config = ConfigFile.load_config()

    page.goto(live_homepage_server)

    for link in config.get_links(host="localhost:8000"):
        expect(page.locator(f'[data-title="{link.title}"]')).to_be_visible()

    page.locator("#search").fill("ste")

    expect(page.locator('[data-title="Steve"]')).to_be_visible()
    expect(page.locator('[data-title="TechMeme"]')).to_be_hidden()
    expect(page.locator('[data-title="Mastodon"]')).to_be_hidden()

    page.locator("#search").fill("tech meme")

    expect(page.locator('[data-title="TechMeme"]')).to_be_visible()
    expect(page.locator('[data-title="Steve"]')).to_be_hidden()
    expect(page.locator('[data-title="Mastodon"]')).to_be_hidden()

    page.locator("#search").fill("")

    for link in config.get_links(host="localhost:8000"):
        expect(page.locator(f'[data-title="{link.title}"]')).to_be_visible()


def test_search_enter_submits_to_duckduckgo(
    page: Page, live_homepage_server: str
) -> None:
    """Submitting the search field still uses the DuckDuckGo form action."""
    page.route(
        "https://duckduckgo.com/**",
        lambda route: route.fulfill(status=200, body="duckduckgo"),
    )

    page.goto(live_homepage_server)
    page.locator("#search").fill("ste")
    page.locator("#search").press("Enter")

    page.wait_for_url("https://duckduckgo.com/?q=ste")
