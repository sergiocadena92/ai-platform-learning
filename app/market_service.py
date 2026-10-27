import asyncio

from fastapi import FastAPI, HTTPException

app = FastAPI()


MARKETS = {
    "US": True,
    "CA": True,
    "UK": False,
}


@app.get("/markets/{country}")
async def get_market(country: str):
    await asyncio.sleep(2)

    country = country.upper()
    if country == "DE":
        raise HTTPException(
            status_code=500,
            detail="Internal market service error",
        )
    if country not in MARKETS:
        raise HTTPException(
            status_code=404,
            detail="Market not found",
        )

    return {
        "country": country,
        "enabled": MARKETS[country],
    }
