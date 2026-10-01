import contextlib
from fastapi import FastAPI
from .core.config import settings
from .core.logger import setup_logging
from .api.routes import router as api_router
from .events.consumer import InventoryEventConsumer

setup_logging()
consumer_thread = InventoryEventConsumer()

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    """Manages the lifecycle of the FastAPI application, starting the Kafka consumer thread on boot and gracefully stopping it on shutdown."""
    consumer_thread.start()
    yield
    consumer_thread.stop()
    consumer_thread.join(timeout=5.0)

def create_app() -> FastAPI:
    """Instantiates the FastAPI application, registers API routes, and optionally sets up Prometheus metrics and OpenTelemetry tracing."""
    app = FastAPI(title=settings.app_name, version=settings.app_version, debug=settings.debug, lifespan=lifespan)
    app.include_router(api_router)
    
    # Prometheus Metrics
    try:
        from prometheus_fastapi_instrumentator import Instrumentator
        Instrumentator().instrument(app).expose(app)
    except ImportError:
        pass
        
    # OpenTelemetry Tracing
    try:
        from shared.observability.tracing import setup_tracing
        setup_tracing(app, "inventory_service")
    except Exception as e:
        pass
        
    return app

app = create_app()
