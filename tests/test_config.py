import pytest
from pydantic import ValidationError

from app.config import get_settings


@pytest.fixture(autouse=True)
def clear_settings_cache():
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_environment_variable_overrides_settings(monkeypatch):
    monkeypatch.setenv(
        "APP_MARKET_SERVICE_TIMEOUT_SECONDS",
        "8",
    )

    settings = get_settings()

    assert settings.market_service_timeout_seconds == 8.0


def test_invalid_timeout_configuration(monkeypatch):
    monkeypatch.setenv(
        "APP_MARKET_SERVICE_TIMEOUT_SECONDS",
        "banana",
    )

    with pytest.raises(ValidationError):
        get_settings()


def test_timeout_must_be_positive(monkeypatch):
    monkeypatch.setenv(
        "APP_MARKET_SERVICE_TIMEOUT_SECONDS",
        "0",
    )

    with pytest.raises(ValidationError):
        get_settings()
