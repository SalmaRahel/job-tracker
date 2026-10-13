import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from src.cv_generation.schemas import CVContent, CVPalette, CVTemplate
from src.cv_generation.utils import compute_idempotency_key
from src.profile.schemas import ProfileResponse


@pytest.fixture()
def client(db):
    from src.main import app

    return TestClient(app)


@pytest.fixture()
def headers(client):
    r = client.post("/register", json={"email": "style@example.com", "password": "Passw0rd!x"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture()
def job_id(client, headers):
    created = client.post("/jobs/", json={"company_name": "Acme", "position": "Dev", "location": "Cairo"}, headers=headers)
    return created.json()["id"]


@pytest.fixture()
def stream(monkeypatch):
    sent = []

    class FakeRedis:
        def xadd(self, name, fields):
            sent.append(fields)

    monkeypatch.setattr("src.cv_generation.router.r", FakeRedis())
    monkeypatch.setattr("src.cv_generation.router.check_and_set_cooldown", lambda *a: True)
    return sent


@pytest.mark.parametrize(
    "body",
    [
        {"template": "fancy"},
        {"palette": "neon"},
        {"template": "colored", "palette": "<script>"},
        {"template": "colored", "palette": "red; background:url(x)"},
        {"template": "colored", "extra": 1},
        {"template": None},
    ],
)
def test_invalid_body_is_rejected(client, headers, job_id, stream, body):
    response = client.post(f"/jobs/{job_id}/generate-cv", json=body, headers=headers)
    assert response.status_code == 422
    assert stream == []


def test_missing_body_uses_defaults(client, headers, job_id, stream):
    response = client.post(f"/jobs/{job_id}/generate-cv", headers=headers)
    assert response.status_code == 202
    assert stream[0]["template"] == "colored"
    assert stream[0]["palette"] == "dark_gray_blue"


def test_valid_body_is_queued(client, headers, job_id, stream):
    body = {"template": "colored", "palette": "frosted_mint"}
    assert client.post(f"/jobs/{job_id}/generate-cv", json=body, headers=headers).status_code == 202
    assert (stream[0]["template"], stream[0]["palette"]) == ("colored", "frosted_mint")


def profile():
    return ProfileResponse(id=1, full_name="Ann", email="a@gmail.com", skills=["Python", "SQL", "Docker"])


def test_key_changes_with_template_and_palette():
    p = profile()
    base = compute_idempotency_key(1, p, CVTemplate.COLORED, CVPalette.DARK_GRAY_BLUE)
    assert base == compute_idempotency_key(1, p, CVTemplate.COLORED, CVPalette.DARK_GRAY_BLUE)
    assert base != compute_idempotency_key(1, p, CVTemplate.COLORED, CVPalette.FROSTED_MINT)
    assert base != compute_idempotency_key(1, p, CVTemplate.PLAIN, CVPalette.DARK_GRAY_BLUE)
    assert base != compute_idempotency_key(2, p, CVTemplate.COLORED, CVPalette.DARK_GRAY_BLUE)


def test_palette_is_ignored_for_plain_key():
    p = profile()
    assert compute_idempotency_key(1, p, CVTemplate.PLAIN, CVPalette.LIGHT_GRAY) == compute_idempotency_key(
        1, p, CVTemplate.PLAIN, CVPalette.FROSTED_MINT
    )


def test_colored_render_emits_palette_variables():
    from src.cv_generation.service import render_cv_html

    content = CVContent(summary="s")
    html = render_cv_html(profile(), content, CVTemplate.COLORED, CVPalette.FROSTED_MINT)
    assert "--accent: #c2e9ff" in html
    assert "--accent-light: #3a4750" in html
    assert "--_note" not in html
    assert "Python" in html


def test_plain_render_has_no_palette_variables():
    from src.cv_generation.service import render_cv_html

    html = render_cv_html(profile(), CVContent(summary="s"), CVTemplate.PLAIN, CVPalette.FROSTED_MINT)
    assert "--accent" not in html


def test_same_style_reuses_pdf_and_style_change_renders_again(job_id, db, monkeypatch):
    from src.auth.models import User
    from src.cv_generation import service
    from src.jobs.models import Job
    from src.profile.models import Profile, Skill

    owner = db.query(Job).filter(Job.id == job_id).first().user_id
    row = Profile(full_name="Ann", email="a@gmail.com", user_id=owner)
    db.add(row)
    db.flush()
    db.add_all([Skill(name=n, profile_id=row.id) for n in ("Python", "SQL", "Docker")])
    db.commit()

    calls = {"gemini": 0, "render": 0}

    def fake_gemini(*a):
        calls["gemini"] += 1
        return object()

    def fake_pdf(html):
        calls["render"] += 1
        return b"%PDF"

    monkeypatch.setattr(service, "generate_cv_content", fake_gemini)
    monkeypatch.setattr(service, "render_cv_html", lambda *a: "<html></html>")
    monkeypatch.setattr(service, "render_cv_pdf", fake_pdf)
    monkeypatch.setattr(service, "upload_cv_to_s3", lambda pdf, key: key)

    first = service.cv_generation(job_id, CVTemplate.COLORED, CVPalette.DARK_GRAY_BLUE, db)
    again = service.cv_generation(job_id, CVTemplate.COLORED, CVPalette.DARK_GRAY_BLUE, db)
    assert again.s3_key == first.s3_key
    assert calls == {"gemini": 1, "render": 1}

    other = service.cv_generation(job_id, CVTemplate.COLORED, CVPalette.LIGHT_GRAY, db)
    assert other.s3_key != first.s3_key
    assert calls == {"gemini": 2, "render": 2}

    plain = service.cv_generation(job_id, CVTemplate.PLAIN, CVPalette.LIGHT_GRAY, db)
    assert plain.s3_key not in {first.s3_key, other.s3_key}
    assert db.execute(text("SELECT count(*) FROM cv_generations WHERE job_id = :j"), {"j": job_id}).scalar() == 1
