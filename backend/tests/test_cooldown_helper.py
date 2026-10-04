import pytest

from src.background_jobs import redis_client
from src.background_jobs.redis_client import check_and_set_cooldown
from src.config import settings


class FakeRedis:
    def __init__(self):
        self.store = {}
        self.calls = []

    def set(self, key, value, nx=False, ex=None):
        self.calls.append((key, ex))
        if nx and key in self.store:
            return None
        self.store[key] = value
        return True


@pytest.fixture()
def fake_redis(monkeypatch):
    fake = FakeRedis()
    monkeypatch.setattr(redis_client, "r", fake)
    return fake


@pytest.mark.parametrize("action", ["analyze", "generate_cv"])
def test_existing_callers_keep_key_format_and_default_ttl(fake_redis, action):
    assert check_and_set_cooldown(7, 3, action) is True
    assert fake_redis.calls == [(f"cooldown:{action}:7:3", settings.action_cooldown_seconds)]
    assert check_and_set_cooldown(7, 3, action) is False


def test_explicit_ttl_is_used(fake_redis):
    assert check_and_set_cooldown(7, 0, "job_search_ask", 5) is True
    assert fake_redis.calls == [("cooldown:job_search_ask:7:0", 5)]


def test_actions_do_not_share_keys(fake_redis):
    assert check_and_set_cooldown(7, 0, "analyze") is True
    assert check_and_set_cooldown(7, 0, "job_search_ask", 5) is True
    assert len(fake_redis.store) == 2
