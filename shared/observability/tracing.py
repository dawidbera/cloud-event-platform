from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.confluent_kafka import ConfluentKafkaInstrumentor

def setup_tracing(app, service_name: str):
    """Initializes OpenTelemetry tracing providers and instruments FastAPI and Confluent Kafka clients for distributed tracing."""
    provider = TracerProvider()
    
    # Export to console for MVP (could be Jaeger/Zipkin in production)
    processor = BatchSpanProcessor(ConsoleSpanExporter())
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    
    FastAPIInstrumentor.instrument_app(app)
    ConfluentKafkaInstrumentor().instrument()
