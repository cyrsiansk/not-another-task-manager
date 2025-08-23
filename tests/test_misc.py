from starlette.testclient import TestClient

from app.main import health, app


def test_health_endpoint_function():
    assert health() == {"status": "ok"}


def test_swagger_docs_endpoint():
    endpoint = "/docs"
    with TestClient(app) as client:
        assert client.get(endpoint).status_code == 200
