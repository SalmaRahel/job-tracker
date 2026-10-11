from datetime import date

import pytest
from fastapi.testclient import TestClient

from src.jobs.stats import month_start

STATUSES = ["Saved", "Applied", "Online Assessment", "Interview", "Final Interview", "Offer", "Rejected", "Withdrawn"]


@pytest.fixture()
def client(db):
    from src.main import app

    return TestClient(app)


def register(client, email):
    r = client.post("/register", json={"email": email, "password": "Passw0rd!x"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def add(client, headers, status="Saved", applied=None):
    body = {"company_name": "Acme", "position": "Dev", "location": "Cairo", "status": status}
    if applied:
        body["application_date"] = applied.isoformat()
    assert client.post("/jobs/", json=body, headers=headers).status_code == 201


def stats(client, headers):
    res = client.get("/jobs/stats", headers=headers)
    assert res.status_code == 200, res.text
    return res.json()


def test_empty_account_returns_zeros(client):
    data = stats(client, register(client, "empty@example.com"))
    assert data["total"] == 0
    assert data["by_status"] == {status: 0 for status in STATUSES}
    assert len(data["monthly"]) == 6
    assert all(item["count"] == 0 for item in data["monthly"])


def test_counts_are_correct(client):
    headers = register(client, "counts@example.com")
    today = date.today()
    this_month = today.replace(day=1)
    last_month = month_start(today, -1)
    five_ago = month_start(today, -5)
    outside = month_start(today, -6)
    future = month_start(today, 1)

    add(client, headers, "Saved")
    add(client, headers, "Applied", this_month)
    add(client, headers, "Applied", this_month)
    add(client, headers, "Interview", last_month)
    add(client, headers, "Offer", five_ago)
    add(client, headers, "Rejected", outside)
    add(client, headers, "Withdrawn", future)

    data = stats(client, headers)
    assert data["total"] == 7
    assert data["by_status"]["Saved"] == 1
    assert data["by_status"]["Applied"] == 2
    assert data["by_status"]["Interview"] == 1
    assert data["by_status"]["Offer"] == 1
    assert data["by_status"]["Online Assessment"] == 0
    assert sum(data["by_status"].values()) == 7

    months = {item["month"]: item["count"] for item in data["monthly"]}
    assert list(months) == [month_start(today, offset).strftime("%Y-%m") for offset in range(-5, 1)]
    assert months[this_month.strftime("%Y-%m")] == 2
    assert months[last_month.strftime("%Y-%m")] == 1
    assert months[five_ago.strftime("%Y-%m")] == 1
    assert sum(months.values()) == 4


def test_other_users_jobs_are_not_counted(client):
    mine = register(client, "mine@example.com")
    other = register(client, "other@example.com")
    add(client, other, "Offer", date.today())
    add(client, other, "Applied", date.today())
    add(client, mine, "Saved")

    data = stats(client, mine)
    assert data["total"] == 1
    assert data["by_status"]["Offer"] == 0
    assert sum(item["count"] for item in data["monthly"]) == 0


def test_stats_needs_a_token(client):
    assert client.get("/jobs/stats").status_code == 401


def test_stats_is_not_read_as_a_job_id(client):
    headers = register(client, "route@example.com")
    assert client.get("/jobs/stats", headers=headers).json()["total"] == 0
    assert client.get("/jobs/0", headers=headers).status_code == 404


def test_month_start_wraps_the_year():
    assert month_start(date(2026, 2, 15), -5) == date(2025, 9, 1)
    assert month_start(date(2026, 12, 31), 1) == date(2027, 1, 1)
