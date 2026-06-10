import logging

from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

from app.core.config import Settings

logger = logging.getLogger(__name__)


def setup_observability(settings: Settings, app) -> None:
    otel_enabled = getattr(settings, "OTEL_ENABLED", True)
    if not otel_enabled:
        logger.info("OpenTelemetry disabled by configuration")
        return
    resource = Resource.create(
        attributes={
            "service.name": "activia-trace",
            "service.version": "0.1.0",
        }
    )
    provider = TracerProvider(resource=resource)
    processor = BatchSpanProcessor(ConsoleSpanExporter())
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    FastAPIInstrumentor.instrument_app(app)
    logger.info("OpenTelemetry initialized for FastAPI")
