import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(db):
    from src.main import app

    yield TestClient(app)
    app.dependency_overrides.clear()


def test_health_ok_without_auth(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_health_returns_503_when_database_fails(client):
    from src.database import get_db
    from src.main import app

    class BrokenSession:
        def execute(self, *args, **kwargs):
            raise RuntimeError("database down")

    app.dependency_overrides[get_db] = lambda: BrokenSession()
    r = client.get("/health")
    assert r.status_code == 503
    assert r.json() == {"status": "unavailable"}
