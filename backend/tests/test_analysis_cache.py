import pytest

from src.matching import cache, service
from src.matching.schemas import JDExtraction, MatchingOutput
from src.profile.schemas import ProfileResponse


class FakeRedis:
    def __init__(self):
        self.data = {}
        self.ttl = {}

    def get(self, key):
        return self.data.get(key)

    def set(self, key, value, ex=None):
        self.data[key] = value
        self.ttl[key] = ex


class BrokenRedis:
    def get(self, key):
        raise ConnectionError("redis down")

    def set(self, key, value, ex=None):
        raise ConnectionError("redis down")


@pytest.fixture()
def redis_fake(monkeypatch):
    fake = FakeRedis()
    monkeypatch.setattr(cache, "r", fake)
    return fake


@pytest.fixture()
def gemini_calls(monkeypatch):
    calls = {"extract": 0, "match": 0}

    def extract(text):
        calls["extract"] += 1
        return JDExtraction(required_skills=["SQL"], nice_to_have_skills=[], experience_level="entry")

    def match(jd, profile):
        calls["match"] += 1
        return MatchingOutput(score=81, missing_requirements=["Docker"])

    monkeypatch.setattr(service, "extract_jd", extract)
    monkeypatch.setattr(service, "run_matching", match)
    return calls


@pytest.fixture()
def setup(db):
    from src.auth.models import User
    from src.jobs.models import ApplicationStatus, Job
    from src.profile.models import Profile, Skill

    user = User(email="cache@example.com", hashed_password="x")
    db.add(user)
    db.flush()
    profile = Profile(full_name="Ann", email="ann@gmail.com", user_id=user.id)
    db.add(profile)
    db.flush()
    for name in ["Python", "sql", "Docker"]:
        db.add(Skill(name=name, profile_id=profile.id))
    job = Job(company_name="Acme", position="Dev", location="Cairo", job_description="Python and SQL",
              status=ApplicationStatus.SAVED, user_id=user.id)
    db.add(job)
    db.commit()
    return job.id


def make_profile(skills):
    return ProfileResponse(id=1, full_name="Ann", email="ann@gmail.com", skills=skills)


def test_miss_calls_gemini_and_stores(db, setup, redis_fake, gemini_calls):
    result = service.analyze_job(setup, db)
    assert gemini_calls == {"extract": 1, "match": 1}
    assert result.score == 81
    assert len(redis_fake.data) == 1
    key, value = next(iter(redis_fake.data.items()))
    assert key.startswith("analysis_cache:")
    assert MatchingOutput.model_validate_json(value).score == 81
    assert redis_fake.ttl[key] == 30 * 24 * 60 * 60


def test_hit_skips_gemini_and_replaces_row(db, setup, redis_fake, gemini_calls):
    first = service.analyze_job(setup, db)
    second = service.analyze_job(setup, db)
    assert gemini_calls == {"extract": 1, "match": 1}
    assert second.score == first.score == 81
    assert second.missing_requirements == ["Docker"]
    from src.matching.models import MatchResult

    assert db.query(MatchResult).filter(MatchResult.job_id == setup).count() == 1


def test_changed_jd_changes_key():
    profile = make_profile(["Python", "SQL", "Docker"])
    assert cache.cache_key("jd one", profile) != cache.cache_key("jd two", profile)


def test_changed_skill_changes_key():
    a = make_profile(["Python", "SQL", "Docker"])
    b = make_profile(["Python", "SQL", "Kubernetes"])
    assert cache.cache_key("jd", a) != cache.cache_key("jd", b)


def test_skill_order_and_case_do_not_change_key():
    a = make_profile(["Python", "SQL", "Docker"])
    b = make_profile(["docker", "python", "sql"])
    c = make_profile(["SQL", "Docker", "Python"])
    assert cache.cache_key("jd", a) == cache.cache_key("jd", b)
    assert cache.cache_key("jd", a) == cache.cache_key("jd", c)


def test_prompt_version_change_invalidates(monkeypatch):
    profile = make_profile(["Python", "SQL", "Docker"])
    old = cache.cache_key("jd", profile)
    monkeypatch.setattr(cache, "PROMPT_VERSION", "analysis-v2")
    assert cache.cache_key("jd", profile) != old


def test_failed_analysis_is_not_cached(db, setup, redis_fake, monkeypatch):
    def boom(text):
        raise RuntimeError("gemini down")

    monkeypatch.setattr(service, "extract_jd", boom)
    with pytest.raises(RuntimeError):
        service.analyze_job(setup, db)
    assert redis_fake.data == {}


def test_invalid_cache_entry_is_ignored(db, setup, redis_fake, gemini_calls):
    key = cache.cache_key("Python and SQL", ProfileResponse.model_validate(
        db.query(__import__("src.profile.models", fromlist=["Profile"]).Profile).first()))
    redis_fake.data[key] = '{"score": 500, "missing_requirements": []}'
    result = service.analyze_job(setup, db)
    assert gemini_calls["match"] == 1
    assert result.score == 81


def test_redis_failure_does_not_fail_the_job(db, setup, monkeypatch, gemini_calls):
    monkeypatch.setattr(cache, "r", BrokenRedis())
    result = service.analyze_job(setup, db)
    assert result.score == 81
    assert gemini_calls == {"extract": 1, "match": 1}
