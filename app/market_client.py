import httpx
import logging

from app.exceptions import MarketNotFound, MarketServiceUnavailable
from app.models import MarketStatus
from fastapi import Request

logger = logging.getLogger(__name__)


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
            logger.debug(
                "Market status received",
                extra={
                    "country": country,
                    "status_code": response.status_code,
                },
            )

            return MarketStatus.model_validate(response.json())

        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                logger.warning(
                    "Market not found",
                    extra={
                        "country": country,
                        "status_code": 404,
                    },
                )
                raise MarketNotFound(country) from exc
            logger.exception(
                "Market service returned an error",
                extra={
                    "country": country,
                    "status_code": exc.response.status_code,
                },
            )
            raise MarketServiceUnavailable() from exc

        except httpx.RequestError as exc:
            logger.exception(
                "Market service request failed country=%s",
                country,
            )
            raise MarketServiceUnavailable() from exc


def get_market_client(request: Request) -> MarketClient:
    return MarketClient(request.app.state.http_client)
