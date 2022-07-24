""" tests for homepage app """

from fastapi.testclient import TestClient
from homepage import app


def test_homepage() -> None:
    """ tests homepage """
    client = TestClient(app)

    assert client.get("/")

def test_config() -> None:
    """ tests something """
    client = TestClient(app)

    assert client.get("/config")
