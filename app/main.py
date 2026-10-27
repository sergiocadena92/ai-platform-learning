from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.config import get_settings


from app.exceptions import (
    MarketNotFound,
    MarketServiceUnavailable,
)
from app.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.state.http_client = httpx.AsyncClient(
        base_url=str(settings.market_service_base_url),
        timeout=settings.market_service_timeout_seconds,
    )

    try:
        yield
    finally:
        await app.state.http_client.aclose()


app = FastAPI(lifespan=lifespan)
app.include_router(router)


@app.exception_handler(MarketNotFound)
async def market_not_found_handler(
    _request: Request,
    exc: MarketNotFound,
):
    return JSONResponse(
        status_code=404,
        content={
            "detail": str(exc),
        },
    )


@app.exception_handler(MarketServiceUnavailable)
async def market_service_unavailable_handler(
    _request: Request,
    exc: MarketServiceUnavailable,
):
    return JSONResponse(
        status_code=503,
        content={
            "detail": str(exc),
        },
    )
