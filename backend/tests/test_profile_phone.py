import pytest
from fastapi.testclient import TestClient

EXPERIENCE = [{"title": "Dev", "company": "Acme", "duration": "2024", "description": "Built things"}]


@pytest.fixture()
def client(db):
    from src.main import app

    return TestClient(app)


@pytest.fixture()
def headers(client):
    r = client.post("/register", json={"email": "phone@example.com", "password": "Passw0rd!x"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def body(phone):
    return {"full_name": "Ann", "email": "ann@example.com", "phone": phone, "experience_json": EXPERIENCE}


@pytest.mark.parametrize("phone", ["+212 6 12 34 56 78", "0612345678", "(555) 123-4567", "+1.555.123.4567", "  0612345678  "])
def test_create_accepts_valid_phone(client, headers, phone):
    res = client.post("/profile/", json=body(phone), headers=headers)
    assert res.status_code == 201, res.text
    assert res.json()["phone"] == phone.strip()


@pytest.mark.parametrize("phone", ["GHHJJJH", "123", "12ab5678901", "+212+612345678", "0612-345-678-9012-3456", "0612 345"])
def test_create_rejects_invalid_phone(client, headers, phone):
    res = client.post("/profile/", json=body(phone), headers=headers)
    assert res.status_code == 422
    assert res.json()["detail"][0]["msg"] == "Enter a valid phone number"


@pytest.mark.parametrize("phone", [None, "", "   "])
def test_create_allows_empty_phone(client, headers, phone):
    res = client.post("/profile/", json=body(phone), headers=headers)
    assert res.status_code == 201
    assert res.json()["phone"] is None


def test_update_validates_phone(client, headers):
    assert client.post("/profile/", json=body(None), headers=headers).status_code == 201
    ok = client.put("/profile/", json={"phone": "0612345678"}, headers=headers)
    assert ok.status_code == 200 and ok.json()["phone"] == "0612345678"

    bad = client.put("/profile/", json={"phone": "12ab5678901"}, headers=headers)
    assert bad.status_code == 422
    assert bad.json()["detail"][0]["msg"] == "Enter a valid phone number"
    assert client.get("/profile/", headers=headers).json()["phone"] == "0612345678"

    cleared = client.put("/profile/", json={"phone": ""}, headers=headers)
    assert cleared.status_code == 200 and cleared.json()["phone"] is None
