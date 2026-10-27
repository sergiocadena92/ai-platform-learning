import httpx

from app.exceptions import MarketNotFound, MarketServiceUnavailable
from app.models import MarketStatus
from fastapi import Request


class MarketClient:

    def __init__(
        self,
        http_client: httpx.AsyncClient,
    ):
        self.http_client = http_client

    async def get_market_status(self, country: str) -> MarketStatus:
        try:
            response = await self.http_client.get(f"/markets/{country}")

            response.raise_for_status()

            return MarketStatus.model_validate(response.json())

        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                raise MarketNotFound(country) from exc
            raise MarketServiceUnavailable() from exc

        except httpx.RequestError as exc:
            raise MarketServiceUnavailable() from exc


def get_market_client(request: Request) -> MarketClient:
    return MarketClient(request.app.state.http_client)
