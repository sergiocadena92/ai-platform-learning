from typing import Protocol

from app.models import MarketStatus


class MarketClientProtocol(Protocol):
    async def get_market_status(
        self,
        country: str,
    ) -> MarketStatus:
        ...