from app.main import health


def test_health_endpoint_function():
    assert health() == {"status": "ok"}
