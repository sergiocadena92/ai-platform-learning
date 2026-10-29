from prometheus_client import (
    CollectorRegistry,
    generate_latest,
)

from app.metrics import Metrics


def test_http_requests_counter():
    registry = CollectorRegistry()
    metrics = Metrics(registry)

    metrics.http_requests_total.labels(
        method="POST",
        path="/products/validate",
        status_code="200",
    ).inc()

    output = generate_latest(registry).decode("utf-8")

    assert (
        "http_requests_total"
        '{method="POST",'
        'path="/products/validate",'
        'status_code="200"} 1.0' in output
    )


def test_http_request_duration_histogram():
    registry = CollectorRegistry()
    metrics = Metrics(registry)

    metrics.http_request_duration_seconds.labels(
        method="POST",
        path="/products/validate",
    ).observe(2.0)

    output = generate_latest(registry).decode("utf-8")

    assert (
        "http_request_duration_seconds_count"
        '{method="POST",'
        'path="/products/validate"} 1.0' in output
    )

    assert (
        "http_request_duration_seconds_sum"
        '{method="POST",'
        'path="/products/validate"} 2.0' in output
    )
