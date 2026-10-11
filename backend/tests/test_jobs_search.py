import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(db):
    from src.main import app

    return TestClient(app)


@pytest.fixture()
def headers(client):
    r = client.post("/register", json={"email": "search@example.com", "password": "Passw0rd!x"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def add(client, headers, company, position="Intern", location="Cairo", description=None):
    body = {"company_name": company, "position": position, "location": location, "job_description": description}
    res = client.post("/jobs/", json=body, headers=headers)
    assert res.status_code == 201
    return res.json()["id"]


def find(client, headers, search):
    res = client.get("/jobs/", params={"search": search}, headers=headers)
    assert res.status_code == 200
    return [job["company_name"] for job in res.json()["items"]]


def test_partial_company_word(client, headers):
    add(client, headers, "Microsoft")
    add(client, headers, "Google")
    assert find(client, headers, "mi") == ["Microsoft"]
    assert find(client, headers, "CROSOF") == ["Microsoft"]


def test_partial_position_word(client, headers):
    add(client, headers, "Acme", position="Software Engineer")
    add(client, headers, "Other", position="Designer")
    assert find(client, headers, "soft") == ["Acme"]
    assert find(client, headers, "engi") == ["Acme"]
    assert find(client, headers, "soft engi") == ["Acme"]


def test_partial_location_word(client, headers):
    add(client, headers, "Acme", location="Berlin, Germany")
    add(client, headers, "Other", location="Cairo")
    assert find(client, headers, "berl") == ["Acme"]
    assert find(client, headers, "germ") == ["Acme"]


def test_whole_word_still_searches_description(client, headers):
    add(client, headers, "Acme", description="We use kubernetes daily")
    add(client, headers, "Other", description="We use docker")
    assert find(client, headers, "kubernetes") == ["Acme"]


@pytest.mark.parametrize("text", ["%", "_", "\\", "100%", "a_c"])
def test_like_wildcards_are_literal(client, headers, text):
    add(client, headers, "Acme")
    add(client, headers, "Abc")
    assert find(client, headers, text) == []


def test_literal_percent_and_underscore_match(client, headers):
    add(client, headers, "Acme", position="100% remote")
    add(client, headers, "Other", position="snake_case dev")
    add(client, headers, "Plain")
    assert find(client, headers, "100%") == ["Acme"]
    assert find(client, headers, "e_c") == ["Other"]


def test_search_keeps_keyset_pagination(client, headers):
    for i in range(25):
        add(client, headers, f"Acme {i}")
    add(client, headers, "Unrelated")
    first = client.get("/jobs/", params={"search": "acm"}, headers=headers).json()
    assert len(first["items"]) == 20 and first["has_more"] is True
    cursor = first["next_cursor"]
    second = client.get("/jobs/", params={
        "search": "acm", "last_seen_created_at": cursor["created_at"], "last_seen_id": cursor["id"],
    }, headers=headers).json()
    assert len(second["items"]) == 5 and second["has_more"] is False
    ids = [j["id"] for j in first["items"] + second["items"]]
    assert len(set(ids)) == 25


def test_search_stays_per_user(client, headers):
    add(client, headers, "Microsoft")
    other = client.post("/register", json={"email": "other@example.com", "password": "Passw0rd!x"})
    other_headers = {"Authorization": f"Bearer {other.json()['access_token']}"}
    assert find(client, other_headers, "micro") == []
