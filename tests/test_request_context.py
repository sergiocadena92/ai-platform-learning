import asyncio
import httpx

from app.main import app
from app.models import MarketStatus
from app.request_context import request_id_var


class ConcurrentFakeMarketClient:
    def __init__(self):
        self.observed_contexts = []

    async def get_market_status(
        self,
        country: str,
    ) -> MarketStatus:
        await asyncio.sleep(0.01)

        self.observed_contexts.append(
            (
                country,
                request_id_var.get(),
            )
        )

        return MarketStatus(
            country=country,
            enabled=True,
        )


def test_request_id_is_isolated_between_concurrent_requests(
    override_market_client,
):
    fake_client = ConcurrentFakeMarketClient()

    override_market_client(fake_client)

    async def run_test():
        transport = httpx.ASGITransport(
            app=app,
        )

        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://test",
        ) as client:

            async def send_request(
                request_id: str,
                country: str,
            ):
                payload = {
                    "product": {
                        "sku": f"PIXEL-{country}",
                        "price": 799,
                        "stock": 10,
                        "countries": [
                            "US",
                            "CA",
                            "UK",
                        ],
                    },
                    "country": country,
                }

                return await client.post(
                    "/products/validate",
                    json=payload,
                    headers={
                        "X-Request-ID": request_id,
                    },
                )

            responses = await asyncio.gather(
                send_request(
                    "request-us",
                    "US",
                ),
                send_request(
                    "request-ca",
                    "CA",
                ),
                send_request(
                    "request-uk",
                    "UK",
                ),
            )

        return responses

    responses = asyncio.run(run_test())

    assert [response.headers["X-Request-ID"] for response in responses] == [
        "request-us",
        "request-ca",
        "request-uk",
    ]

    assert set(fake_client.observed_contexts) == {
        ("US", "request-us"),
        ("CA", "request-ca"),
        ("UK", "request-uk"),
    }
