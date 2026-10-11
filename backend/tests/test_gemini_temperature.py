import json

import pytest

from src import gemini
from src.cv_generation import service as cv_service
from src.matching import service as matching_service
from src.matching.schemas import JDExtraction
from src.profile.schemas import ProfileResponse


class FakeModels:
    def __init__(self):
        self.calls = []

    def generate_content(self, **kwargs):
        self.calls.append(kwargs)
        return type("Reply", (), {"text": "ok"})()


@pytest.fixture()
def models(monkeypatch):
    fake = FakeModels()
    monkeypatch.setattr(gemini, "client", type("FakeClient", (), {"models": fake})())
    return fake


def test_wrapper_sends_temperature_when_given(models):
    assert gemini.call_gemini("hi", max_retries=1, model_name="m", temperature=0) == "ok"
    assert models.calls[0]["config"].temperature == 0


def test_wrapper_leaves_config_empty_by_default(models):
    gemini.call_gemini("hi", max_retries=1, model_name="m")
    assert models.calls[0]["config"] is None


@pytest.fixture()
def captured(monkeypatch):
    calls = []

    def fake(prompt, **kwargs):
        calls.append({"prompt": prompt, **kwargs})
        return json.dumps(fake.reply)

    monkeypatch.setattr(matching_service, "call_gemini", fake)
    monkeypatch.setattr(cv_service, "call_gemini", fake)
    fake.calls = calls
    return fake


def profile():
    return ProfileResponse(id=1, full_name="Ann", email="a@gmail.com", skills=["PostgreSQL"])


def test_jd_extraction_uses_temperature_zero(captured):
    captured.reply = {"required_skills": [], "nice_to_have_skills": [], "experience_level": "entry"}
    matching_service.extract_jd("Python dev")
    assert captured.calls[0]["temperature"] == 0


def test_matching_uses_temperature_zero(captured):
    captured.reply = {"score": 70, "missing_requirements": []}
    jd = JDExtraction(required_skills=["SQL"], nice_to_have_skills=[], experience_level="entry")
    matching_service.run_matching(jd, profile())
    assert captured.calls[0]["temperature"] == 0


def test_matching_prompt_counts_equivalent_skills(captured):
    captured.reply = {"score": 70, "missing_requirements": []}
    jd = JDExtraction(required_skills=["SQL"], nice_to_have_skills=[], experience_level="entry")
    matching_service.run_matching(jd, profile())
    assert "PostgreSQL counts as SQL" in captured.calls[0]["prompt"]


def test_cv_generation_keeps_default_temperature(captured):
    captured.reply = {"summary": "Hello"}
    cv_service.generate_cv_content(profile(), "Python dev")
    assert "temperature" not in captured.calls[0]
