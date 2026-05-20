import pytest

from app.config import get_settings
from app.api.dependencies import reset_rate_limiter


@pytest.fixture(autouse=True)
def isolate_local_api_key(monkeypatch):
    monkeypatch.setenv("LOCAL_API_KEY", "")
    get_settings.cache_clear()
    reset_rate_limiter()
    yield
    get_settings.cache_clear()
    reset_rate_limiter()
