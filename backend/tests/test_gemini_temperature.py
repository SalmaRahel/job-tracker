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


def test_wrapper_sends_thinking_level_with_temperature(models):
    gemini.call_gemini("hi", max_retries=1, model_name="m", temperature=0, thinking_level="MINIMAL")
    config = models.calls[0]["config"]
    assert config.temperature == 0
    assert config.thinking_config.thinking_level.value == "MINIMAL"


def test_wrapper_sends_no_thinking_config_by_default(models):
    gemini.call_gemini("hi", max_retries=1, model_name="m", temperature=0)
    assert models.calls[0]["config"].thinking_config is None


def test_wrapper_retry_is_counted(monkeypatch):
    import logging

    from google.genai import errors

    class FlakyModels:
        calls = 0

        def generate_content(self, **kwargs):
            FlakyModels.calls += 1
            if FlakyModels.calls == 1:
                raise errors.APIError(500, {"error": {"message": "boom"}})
            return type("Reply", (), {"text": "ok"})()

    monkeypatch.setattr(gemini, "client", type("FakeClient", (), {"models": FlakyModels()})())
    monkeypatch.setattr(gemini.time, "sleep", lambda seconds: None)
    records = []

    class Collect(logging.Handler):
        def emit(self, record):
            records.append(record.getMessage())

    handler = Collect(level=logging.INFO)
    previous_level = gemini.logger.level
    gemini.logger.disabled = False
    gemini.logger.addHandler(handler)
    gemini.logger.setLevel(logging.INFO)
    try:
        assert gemini.call_gemini("hi", max_retries=2, model_name="m") == "ok"
    finally:
        gemini.logger.removeHandler(handler)
        gemini.logger.setLevel(previous_level)
    assert any("retried=True" in message for message in records)


def test_jd_extraction_and_matching_use_minimal_thinking(captured):
    captured.reply = {"required_skills": [], "nice_to_have_skills": [], "experience_level": "entry"}
    matching_service.extract_jd("Python dev")
    captured.reply = {"score": 70, "missing_requirements": []}
    jd = JDExtraction(required_skills=["SQL"], nice_to_have_skills=[], experience_level="entry")
    matching_service.run_matching(jd, profile())
    assert [c["thinking_level"] for c in captured.calls] == ["MINIMAL", "MINIMAL"]


def test_cv_generation_has_no_thinking_level(captured):
    captured.reply = {"summary": "Hello"}
    cv_service.generate_cv_content(profile(), "Python dev")
    assert "thinking_level" not in captured.calls[0]


class ScriptedModels:
    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.calls = []

    def generate_content(self, **kwargs):
        self.calls.append(kwargs)
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return type("Reply", (), {"text": outcome})()


def scripted(monkeypatch, outcomes):
    from google.genai import errors

    fake = ScriptedModels(outcomes)
    monkeypatch.setattr(gemini, "client", type("FakeClient", (), {"models": fake})())
    monkeypatch.setattr(gemini.time, "sleep", lambda s: None)
    return fake


def server_error(code=503):
    from google.genai import errors

    return errors.ServerError(code, {"error": {"code": code, "message": "busy", "status": "UNAVAILABLE"}})


def client_error(code):
    from google.genai import errors

    return errors.ClientError(code, {"error": {"code": code, "message": "x", "status": "X"}})


def test_503_falls_back_to_flash_lite(monkeypatch, caplog):
    fake = scripted(monkeypatch, [server_error(503), "from-lite"])
    with caplog.at_level("WARNING"):
        result = gemini.call_gemini("p", max_retries=1, model_name="gemini-3.5-flash", temperature=0, thinking_level="minimal")
    assert result == "from-lite"
    assert [c["model"] for c in fake.calls] == ["gemini-3.5-flash", gemini.FALLBACK_MODEL]
    assert fake.calls[1]["contents"] == "p"
    assert fake.calls[1]["config"].temperature == 0
    assert fake.calls[1]["config"].thinking_config.thinking_level.value.lower() == "minimal"
    assert any("gemini-3.5-flash" in r.message and "503" in r.message for r in caplog.records)


def test_429_falls_back_to_flash_lite(monkeypatch):
    fake = scripted(monkeypatch, [client_error(429), "from-lite"])
    assert gemini.call_gemini("p", max_retries=1, model_name="gemini-3.5-flash") == "from-lite"
    assert len(fake.calls) == 2


def test_fallback_does_not_use_up_retries(monkeypatch):
    fake = scripted(monkeypatch, [server_error(), server_error(), "from-lite"])
    assert gemini.call_gemini("p", max_retries=2, model_name="gemini-3.5-flash") == "from-lite"
    assert [c["model"] for c in fake.calls] == ["gemini-3.5-flash", "gemini-3.5-flash", gemini.FALLBACK_MODEL]


def test_both_models_failing_raises_the_original_error(monkeypatch):
    original = server_error(503)
    fake = scripted(monkeypatch, [original, client_error(400)])
    with pytest.raises(Exception) as raised:
        gemini.call_gemini("p", max_retries=1, model_name="gemini-3.5-flash")
    assert raised.value is original
    assert len(fake.calls) == 2


def test_400_does_not_fall_back(monkeypatch):
    fake = scripted(monkeypatch, [client_error(400)])
    with pytest.raises(Exception):
        gemini.call_gemini("p", max_retries=1, model_name="gemini-3.5-flash")
    assert len(fake.calls) == 1


def test_call_already_on_flash_lite_does_not_loop(monkeypatch):
    fake = scripted(monkeypatch, [server_error()])
    with pytest.raises(Exception):
        gemini.call_gemini("p", max_retries=1, model_name=gemini.FALLBACK_MODEL)
    assert len(fake.calls) == 1
