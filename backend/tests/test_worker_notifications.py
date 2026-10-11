import pytest
from sqlalchemy import text


@pytest.fixture()
def job(db):
    from src.auth.models import User
    from src.jobs.models import ApplicationStatus, Job

    user = User(email="worker@example.com", hashed_password="x")
    db.add(user)
    db.flush()
    row = Job(company_name="Acme", position="Dev", location="Cairo", job_description="Python",
              status=ApplicationStatus.SAVED, user_id=user.id)
    db.add(row)
    db.commit()
    return row.id, user.id


@pytest.fixture()
def published(monkeypatch):
    sent = []
    send = lambda user_id, message: sent.append((user_id, message))
    monkeypatch.setattr("src.matching.service.publish_notification", send)
    monkeypatch.setattr("src.cv_generation.service.publish_notification", send)
    return sent


def boom(*args, **kwargs):
    raise RuntimeError("gemini down")


def test_analysis_success_is_published(job, published, monkeypatch):
    from src.matching import service

    job_id, user_id = job
    monkeypatch.setattr(service, "analyze_job", lambda *a: object())
    service.run_analysis(job_id)
    assert published == [(user_id, f"matching score is ready for user: {user_id}, job_id: {job_id}")]


@pytest.mark.parametrize("outcome", [lambda *a: None, boom])
def test_analysis_failure_is_published(job, published, monkeypatch, outcome):
    from src.matching import service

    job_id, user_id = job
    monkeypatch.setattr(service, "analyze_job", outcome)
    service.run_analysis(job_id)
    assert published == [(user_id, f"matching failed for user: {user_id}, job_id: {job_id}")]


def test_analysis_of_missing_job_publishes_nothing(db, published):
    from src.matching import service

    service.run_analysis(999999)
    assert published == []


def test_cv_success_is_published(job, published, monkeypatch):
    from src.cv_generation import service

    job_id, user_id = job
    monkeypatch.setattr(service, "cv_generation", lambda *a: object())
    service.run_cv_generation(job_id, None)
    assert published == [(user_id, f"cv generated for user: {user_id}, job_id: {job_id}")]


@pytest.mark.parametrize("outcome", [lambda *a: None, boom])
def test_cv_failure_is_published(job, published, monkeypatch, outcome):
    from src.cv_generation import service

    job_id, user_id = job
    monkeypatch.setattr(service, "cv_generation", outcome)
    service.run_cv_generation(job_id, None)
    assert published == [(user_id, f"cv generation failed for user: {user_id}, job_id: {job_id}")]


def test_cv_regeneration_after_profile_change_replaces_the_row(job, db, monkeypatch):
    from src.cv_generation import service
    from src.cv_generation.models import CVGeneration
    from src.profile.models import Profile, Skill

    job_id, user_id = job
    profile = Profile(full_name="Ann", email="a@gmail.com", user_id=user_id)
    db.add(profile)
    db.flush()
    db.add_all([Skill(name=name, profile_id=profile.id) for name in ("Python", "SQL", "Docker")])
    db.commit()

    monkeypatch.setattr(service, "generate_cv_content", lambda *a: object())
    monkeypatch.setattr(service, "render_cv_html", lambda *a: "<html></html>")
    monkeypatch.setattr(service, "render_cv_pdf", lambda html: b"%PDF")
    monkeypatch.setattr(service, "upload_cv_to_s3", lambda pdf, key: key)

    first = service.cv_generation(job_id, None, db)
    again = service.cv_generation(job_id, None, db)
    assert first is not None and again.s3_key == first.s3_key

    profile.city = "Rabat"
    db.commit()
    second = service.cv_generation(job_id, None, db)
    assert second is not None and second.s3_key != first.s3_key

    rows = db.execute(text("SELECT key FROM cv_generations WHERE job_id = :j"), {"j": job_id}).all()
    assert [row.key for row in rows] == [second.s3_key]
    assert db.query(CVGeneration).count() == 1


def test_profile_response_includes_skill_names(db):
    from src.auth.models import User
    from src.profile.models import Profile, Skill
    from src.profile.schemas import ProfileResponse

    user = User(email="skills@example.com", hashed_password="x")
    db.add(user)
    db.flush()
    profile = Profile(full_name="Ann", email="a@gmail.com", user_id=user.id)
    db.add(profile)
    db.flush()
    db.add(Skill(name="Python", profile_id=profile.id))
    db.commit()
    db.refresh(profile)
    assert ProfileResponse.model_validate(profile).skills == ["Python"]
