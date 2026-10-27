import asyncio

import httpx
import pytest

from app import market_client
from app.exceptions import MarketNotFound, MarketServiceUnavailable
from app.market_client import get_market_client
from app.models import MarketStatus
from fastapi import FastAPI, Request


class FakeAsyncClient:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        return None

    async def get(self, url):
        if self.error is not None:
            raise self.error
        return self.response


def make_market_client(*, response=None, error=None):
    client = FakeAsyncClient(response=response, error=error)
    return market_client.MarketClient(client)


def test_get_market_client_returns_market_client():
    app = FastAPI()
    app.state.http_client = FakeAsyncClient()
    request = Request({"type": "http", "app": app})

    result = get_market_client(request)

    assert isinstance(result, market_client.MarketClient)
    assert result.http_client is app.state.http_client


def test_market_client_get_market_status_returns_market_status():
    response = httpx.Response(
        200,
        json={"country": "US", "enabled": True},
        request=httpx.Request("GET", "http://127.0.0.1:8001/markets/US"),
    )
    client = make_market_client(response=response)

    result = asyncio.run(client.get_market_status("US"))

    assert result.country == "US"
    assert result.enabled is True


def test_get_market_status_returns_market_status():
    response = httpx.Response(
        200,
        json={"country": "US", "enabled": True},
        request=httpx.Request("GET", "http://127.0.0.1:8001/markets/US"),
    )
    client = make_market_client(response=response)

    result = asyncio.run(client.get_market_status("US"))

    assert result.country == "US"
    assert result.enabled is True


def test_get_market_status_maps_not_found():
    response = httpx.Response(
        404,
        request=httpx.Request("GET", "http://127.0.0.1:8001/markets/DE"),
    )
    client = make_market_client(response=response)

    with pytest.raises(MarketNotFound) as error:
        asyncio.run(client.get_market_status("DE"))

    assert error.value.country == "DE"
    assert isinstance(error.value.__cause__, httpx.HTTPStatusError)


@pytest.mark.parametrize(
    "response",
    [
        httpx.Response(
            500,
            request=httpx.Request("GET", "http://127.0.0.1:8001/markets/US"),
        ),
        httpx.Response(
            503,
            request=httpx.Request("GET", "http://127.0.0.1:8001/markets/US"),
        ),
    ],
)
def test_get_market_status_maps_http_errors_to_unavailable(response):
    client = make_market_client(response=response)

    with pytest.raises(MarketServiceUnavailable) as error:
        asyncio.run(client.get_market_status("US"))

    assert isinstance(error.value.__cause__, httpx.HTTPStatusError)


def test_get_market_status_maps_request_errors_to_unavailable():
    request = httpx.Request("GET", "http://127.0.0.1:8001/markets/US")
    client = make_market_client(
        error=httpx.ConnectError("connection failed", request=request),
    )

    with pytest.raises(MarketServiceUnavailable) as error:
        asyncio.run(client.get_market_status("US"))

    assert isinstance(error.value.__cause__, httpx.ConnectError)


def test_get_market_status_maps_timeouts_to_unavailable():
    request = httpx.Request("GET", "http://127.0.0.1:8001/markets/US")
    client = make_market_client(
        error=httpx.ReadTimeout("request timed out", request=request),
    )

    with pytest.raises(MarketServiceUnavailable) as error:
        asyncio.run(client.get_market_status("US"))

    assert isinstance(error.value.__cause__, httpx.ReadTimeout)

class FakeMarketNotFoundClient:
    async def get_market_status(
        self,
        country: str,
    ) -> MarketStatus:
        raise MarketNotFound(country)


class FakeMarketUnavailableClient:
    async def get_market_status(
        self,
        country: str,
    ) -> MarketStatus:
        raise MarketServiceUnavailable()