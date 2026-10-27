import asyncio
import time

import httpx


async def validate_product(
    client: httpx.AsyncClient,
    sku: str,
    country: str,
):
    payload = {
        "product": {
            "sku": sku,
            "price": 799,
            "stock": 20,
            "countries": ["US", "CA", "UK"],
        },
        "country": country,
    }

    response = await client.post(
        "http://127.0.0.1:8000/products/validate",
        json=payload,
    )

    return response.json()


async def main():
    start = time.perf_counter()

    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(
            validate_product(client, "PIXEL-US", "US"),
            validate_product(client, "PIXEL-CA", "CA"),
            validate_product(client, "PIXEL-UK", "UK"),
        )

    elapsed = time.perf_counter() - start

    print(results)
    print(f"Elapsed: {elapsed:.2f} seconds")


if __name__ == "__main__":
    asyncio.run(main())