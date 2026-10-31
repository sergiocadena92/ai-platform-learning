from contextlib import asynccontextmanager
import logging
import time
import uuid
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.config import get_settings
from app.request_context import request_id_var
from app.exceptions import (
    MarketNotFound,
    MarketServiceUnavailable,
)
from app.logging_config import configure_logging
from app.routes import router
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    generate_latest,
)
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

from app.tracing import configure_tracing
from app.metrics import METRICS
from fastapi.responses import Response
from opentelemetry.instrumentation.fastapi import (
    FastAPIInstrumentor,
)

logger = logging.getLogger(__name__)

TRACER_PROVIDER = configure_tracing(
    get_settings().service_name
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    configure_logging(settings.log_level)

    http_client = httpx.AsyncClient(
        base_url=str(settings.market_service_base_url),
        timeout=settings.market_service_timeout_seconds,
    )

    HTTPXClientInstrumentor.instrument_client(
        http_client,
        tracer_provider=TRACER_PROVIDER,
    )

    app.state.http_client = http_client

    try:
        yield
    finally:
        HTTPXClientInstrumentor.uninstrument_client(
            http_client
        )
        await http_client.aclose()


app = FastAPI(lifespan=lifespan)
app.include_router(router)


@app.middleware("http")
async def log_requests(
    request: Request,
    call_next,
):
    request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex

    token = request_id_var.set(request_id)

    start = time.perf_counter()

    try:
        response = await call_next(request)
        route_template = get_route_template(request)

        duration_seconds = time.perf_counter() - start

        duration_ms = duration_seconds * 1000

        METRICS.http_requests_total.labels(
            method=request.method,
            path=route_template,
            status_code=response.status_code,
        ).inc()

        METRICS.http_request_duration_seconds.labels(
            method=request.method,
            path=route_template,
        ).observe(duration_seconds)

        response.headers["X-Request-ID"] = request_id

        logger.info(
            "Request completed",
            extra={
                "method": request.method,
                "path": route_template,
                "status_code": response.status_code,
                "duration_ms": round(
                    duration_ms,
                    2,
                ),
            },
        )

        return response

    finally:
        request_id_var.reset(token)


def get_route_template(request: Request) -> str:
    fastapi_scope = request.scope.get("fastapi", {})
    effective_route = fastapi_scope.get("effective_route_context")

    if effective_route is not None:
        return effective_route.path_format

    route = request.scope.get("route")

    if route is not None:
        return getattr(
            route,
            "path_format",
            request.url.path,
        )

    return request.url.path


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


@app.get("/metrics")
async def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )

FastAPIInstrumentor.instrument_app(
    app,
    tracer_provider=TRACER_PROVIDER,
    exclude_spans=[
        "receive",
        "send",
    ],
)