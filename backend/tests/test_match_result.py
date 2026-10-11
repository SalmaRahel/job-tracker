import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(db):
    from src.main import app

    return TestClient(app)


def register(client, email):
    r = client.post("/register", json={"email": email, "password": "Passw0rd!x"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def make_job(client, headers, description="Python and SQL"):
    body = {"company_name": "Acme", "position": "Dev", "location": "Cairo", "job_description": description}
    return client.post("/jobs/", json=body, headers=headers).json()["id"]


def add_result(db, job_id, score=72, missing=("Docker", "AWS")):
    from src.matching.models import MatchResult

    result = MatchResult(job_id=job_id, score=score, missing_requirements=list(missing))
    db.add(result)
    db.commit()
    return result.id


def test_analysis_is_404_until_a_result_exists(client, db):
    headers = register(client, "m1@example.com")
    job_id = make_job(client, headers)
    res = client.get(f"/jobs/{job_id}/analysis", headers=headers)
    assert res.status_code == 404 and res.json()["detail"] == "Analysis not found"

    result_id = add_result(db, job_id)
    res = client.get(f"/jobs/{job_id}/analysis", headers=headers)
    assert res.status_code == 200
    assert res.json() == {"id": result_id, "score": 72, "missing_requirements": ["Docker", "AWS"]}


def test_analysis_of_another_users_job_is_404(client, db):
    owner = register(client, "m2@example.com")
    other = register(client, "m3@example.com")
    job_id = make_job(client, owner)
    add_result(db, job_id)
    res = client.get(f"/jobs/{job_id}/analysis", headers=other)
    assert res.status_code == 404 and res.json()["detail"] == "Job not found"


def test_analysis_needs_login(client):
    assert client.get("/jobs/1/analysis").status_code in (401, 403)


def test_changing_description_deletes_the_match_result(client, db):
    headers = register(client, "m4@example.com")
    job_id = make_job(client, headers)
    add_result(db, job_id)
    res = client.put(f"/jobs/{job_id}", json={"job_description": "Go and Kubernetes"}, headers=headers)
    assert res.status_code == 200
    assert client.get(f"/jobs/{job_id}/analysis", headers=headers).status_code == 404


def test_other_edits_keep_the_match_result(client, db):
    headers = register(client, "m5@example.com")
    job_id = make_job(client, headers)
    add_result(db, job_id)
    assert client.put(f"/jobs/{job_id}", json={"position": "Senior Dev"}, headers=headers).status_code == 200
    assert client.put(f"/jobs/{job_id}", json={"job_description": "Python and SQL"}, headers=headers).status_code == 200
    assert client.get(f"/jobs/{job_id}/analysis", headers=headers).status_code == 200
