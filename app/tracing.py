from opentelemetry import trace
from opentelemetry.sdk.resources import (
    Resource,
    SERVICE_NAME,
)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    SimpleSpanProcessor,
)


def configure_tracing(
    service_name: str,
) -> TracerProvider:
    resource = Resource.create(
        {
            SERVICE_NAME: service_name,
        }
    )

    provider = TracerProvider(
        resource=resource,
    )

    provider.add_span_processor(
        SimpleSpanProcessor(
            ConsoleSpanExporter()
        )
    )

    trace.set_tracer_provider(provider)

    return provider