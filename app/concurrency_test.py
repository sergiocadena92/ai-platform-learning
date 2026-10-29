import asyncio
import time

import httpx


REQUESTS = [
    ("request-us", "US"),
    ("request-ca", "CA"),
    ("request-uk", "UK"),
]


async def validate_product(
    client: httpx.AsyncClient,
    request_id: str,
    country: str,
):
    payload = {
        "product": {
            "sku": f"PIXEL-{country}",
            "price": 799,
            "stock": 10,
            "countries": ["US", "CA", "UK"],
        },
        "country": country,
    }

    response = await client.post(
        "/products/validate",
        json=payload,
        headers={
            "X-Request-ID": request_id,
        },
    )

    return {
        "request_id_sent": request_id,
        "request_id_received": response.headers.get(
            "X-Request-ID"
        ),
        "country": country,
        "status_code": response.status_code,
        "body": response.json(),
    }


async def main():
    async with httpx.AsyncClient(
        base_url="http://127.0.0.1:8000",
    ) as client:
        start = time.perf_counter()

        results = await asyncio.gather(
            *[
                validate_product(
                    client,
                    request_id,
                    country,
                )
                for request_id, country in REQUESTS
            ]
        )

        elapsed = time.perf_counter() - start

    for result in results:
        print(result)

    print(f"Elapsed: {elapsed:.2f} seconds")


if __name__ == "__main__":
    asyncio.run(main())