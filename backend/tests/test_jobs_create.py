import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(db):
    from src.main import app

    return TestClient(app)


@pytest.fixture()
def headers(client):
    r = client.post("/register", json={"email": "create@example.com", "password": "Passw0rd!x"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


BODY = {"company_name": "Acme", "position": "Intern", "location": "Cairo"}


def test_create_saves_status_and_application_date(client, headers):
    body = {**BODY, "status": "Applied", "application_date": "2025-03-28"}
    created = client.post("/jobs/", json=body, headers=headers)
    assert created.status_code == 201
    assert created.json()["status"] == "Applied"
    assert created.json()["application_date"] == "2025-03-28"

    got = client.get(f"/jobs/{created.json()['id']}", headers=headers).json()
    assert got["status"] == "Applied"
    assert got["application_date"] == "2025-03-28"


def test_create_without_status_defaults_to_saved(client, headers):
    created = client.post("/jobs/", json=BODY, headers=headers)
    assert created.status_code == 201
    assert created.json()["status"] == "Saved"
    assert created.json()["application_date"] is None


@pytest.mark.parametrize("status", ["Hired", "applied", "SAVED", ""])
def test_create_rejects_unknown_status(client, headers, status):
    res = client.post("/jobs/", json={**BODY, "status": status}, headers=headers)
    assert res.status_code == 422


@pytest.mark.parametrize("field,limit", [
    ("company_name", 100), ("position", 150), ("location", 50), ("job_link", 250),
])
def test_too_long_fields_return_422_on_create_and_update(client, headers, field, limit):
    too_long = "x" * (limit + 1)
    assert client.post("/jobs/", json={**BODY, field: too_long}, headers=headers).status_code == 422

    ok = client.post("/jobs/", json={**BODY, field: "x" * limit}, headers=headers)
    assert ok.status_code == 201
    res = client.put(f"/jobs/{ok.json()['id']}", json={field: too_long}, headers=headers)
    assert res.status_code == 422
