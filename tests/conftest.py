import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.market_client import get_market_client
from app.models import MarketStatus
from app.config import get_settings


from app.exceptions import (
    MarketNotFound,
    MarketServiceUnavailable,
)


class FakeMarketClient:
    def __init__(
        self,
        enabled: bool = True,
        error: MarketNotFound | MarketServiceUnavailable | None = None,
    ):
        self.enabled = enabled
        self.error = error

    async def get_market_status(self, country: str) -> MarketStatus:
        if isinstance(self.error, MarketNotFound):
            raise MarketNotFound(country)
        if self.error is not None:
            raise self.error

        return MarketStatus(country=country, enabled=self.enabled)


@pytest.fixture
def market_enabled(request):
    return getattr(request, "param", True)


@pytest.fixture
def market_error(request):
    return getattr(request, "param", None)


@pytest.fixture
def test_client(market_enabled, market_error):
    fake_market_client = FakeMarketClient(
        enabled=market_enabled,
        error=market_error,
    )
    app.dependency_overrides[get_market_client] = lambda: fake_market_client

    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.pop(get_market_client, None)


@pytest.fixture(autouse=True)
def clear_settings_cache():
    get_settings.cache_clear()

    yield

    get_settings.cache_clear()