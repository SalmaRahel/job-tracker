import pytest
from fastapi.testclient import TestClient

EXPERIENCE = [{"title": "Dev", "company": "Acme", "duration": "2024", "description": "Built things"}]


@pytest.fixture()
def client(db):
    from src.main import app

    return TestClient(app)


@pytest.fixture()
def headers(client):
    r = client.post("/register", json={"email": "owner@example.com", "password": "Passw0rd!x"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def body(email):
    return {"full_name": "Ann", "email": email, "experience_json": EXPERIENCE}


def message(res):
    return res.json()["detail"][0]["msg"]


@pytest.mark.parametrize("email", ["a@gmail.com", "a.b@univ.ac.ma"])
def test_valid_emails_are_accepted(client, headers, email):
    res = client.post("/profile/", json=body(email), headers=headers)
    assert res.status_code == 201, res.text
    assert res.json()["email"] == email


@pytest.mark.parametrize("email", ["abc", "a@b", "a@@b.com", "a@b..com", "a@.com", "", "a b@gmail.com"])
def test_invalid_emails_are_rejected(client, headers, email):
    res = client.post("/profile/", json=body(email), headers=headers)
    assert res.status_code == 422
    assert message(res) == "Enter a valid email address"


@pytest.mark.parametrize("typo,fixed", [
    ("gmal.com", "gmail.com"), ("gmial.com", "gmail.com"), ("gamil.com", "gmail.com"),
    ("gmail.co", "gmail.com"), ("gmaill.com", "gmail.com"), ("gmai.com", "gmail.com"),
    ("hotmial.com", "hotmail.com"), ("hotmal.com", "hotmail.com"), ("hotnail.com", "hotmail.com"),
    ("outlok.com", "outlook.com"), ("outloook.com", "outlook.com"),
    ("yaho.com", "yahoo.com"), ("yahooo.com", "yahoo.com"),
])
def test_domain_typos_get_a_suggestion(client, headers, typo, fixed):
    res = client.post("/profile/", json=body(f"BOO@{typo}"), headers=headers)
    assert res.status_code == 422
    assert message(res) == f"Did you mean BOO@{fixed}?"


def test_typo_suggestion_ignores_domain_case(client, headers):
    res = client.post("/profile/", json=body("boo@GMAL.com"), headers=headers)
    assert message(res) == "Did you mean boo@gmail.com?"


def test_update_checks_email(client, headers):
    assert client.post("/profile/", json=body("a@gmail.com"), headers=headers).status_code == 201
    typo = client.put("/profile/", json={"email": "BOO@gmal.com"}, headers=headers)
    assert typo.status_code == 422 and message(typo) == "Did you mean BOO@gmail.com?"
    bad = client.put("/profile/", json={"email": "a@b"}, headers=headers)
    assert bad.status_code == 422 and message(bad) == "Enter a valid email address"
    ok = client.put("/profile/", json={"email": "new@univ.ac.ma"}, headers=headers)
    assert ok.status_code == 200 and ok.json()["email"] == "new@univ.ac.ma"
    assert client.put("/profile/", json={"city": "Rabat"}, headers=headers).status_code == 200
