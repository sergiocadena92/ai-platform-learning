from prometheus_client import (
    REGISTRY,
    CollectorRegistry,
    Counter,
    Histogram,
)


class Metrics:
    def __init__(
        self,
        registry: CollectorRegistry = REGISTRY,
    ):
        self.http_requests_total = Counter(
            "http_requests_total",
            "Total number of HTTP requests",
            [
                "method",
                "path",
                "status_code",
            ],
            registry=registry,
        )

        self.http_request_duration_seconds = Histogram(
            "http_request_duration_seconds",
            "HTTP request duration in seconds",
            [
                "method",
                "path",
            ],
            registry=registry,
        )


METRICS = Metrics()