""" tests for homepage app """

from fastapi.testclient import TestClient
from homepage import app


def test_example_function() -> None:
    """ tests something """
    client = TestClient(app)

    assert client.get("/")
