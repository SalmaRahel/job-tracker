"""Proof that enabling RLS did not change the existing /jobs routes (app connection)."""
import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(db):
    from src.main import app

    return TestClient(app)  # no `with`: skips the Redis listener in lifespan


def register(client, email):
    r = client.post("/register", json={"email": email, "password": "Passw0rd!x"})
    assert r.status_code == 201, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_jobs_crud_still_works_and_stays_per_user(client):
    h_a = register(client, "route_a@example.com")
    h_b = register(client, "route_b@example.com")
    body = {"company_name": "Acme", "position": "Intern", "location": "Cairo",
            "job_description": "secret jd", "job_link": "https://x.test"}

    created = client.post("/jobs/", json=body, headers=h_a)
    assert created.status_code == 201
    job_id = created.json()["id"]

    # list + get: user A sees the job, including the columns the read-only role cannot read
    listed = client.get("/jobs/", headers=h_a).json()
    assert [j["id"] for j in listed["items"]] == [job_id]
    got = client.get(f"/jobs/{job_id}", headers=h_a).json()
    assert got["job_description"] == "secret jd" and got["job_link"] == "https://x.test"

    # user B cannot see or touch it (existing app-level check, unchanged)
    assert client.get("/jobs/", headers=h_b).json()["items"] == []
    assert client.get(f"/jobs/{job_id}", headers=h_b).status_code == 404

    # update + delete
    upd = client.put(f"/jobs/{job_id}", json={"status": "Applied"}, headers=h_a)
    assert upd.status_code == 200 and upd.json()["status"] == "Applied"
    assert client.delete(f"/jobs/{job_id}", headers=h_a).status_code == 204
    assert client.get(f"/jobs/{job_id}", headers=h_a).status_code == 404
