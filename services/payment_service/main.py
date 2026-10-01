import contextlib
from fastapi import FastAPI
from .core.config import settings
from .core.logger import setup_logging
from .api.routes import router as api_router
from .events.consumer import PaymentEventConsumer

setup_logging()

# Background consumer
consumer_thread = PaymentEventConsumer()

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan context that spins up the PaymentEventConsumer thread upon application startup and tears it down on exit."""
    # Startup
    consumer_thread.start()
    yield
    # Shutdown
    consumer_thread.stop()
    consumer_thread.join(timeout=5.0)

def create_app() -> FastAPI:
    """Bootstraps the FastAPI instance, mounts routes, and instruments the application with optional metrics and tracing."""
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan
    )
    
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
        setup_tracing(app, "payment_service")
    except Exception as e:
        pass
        
    return app

app = create_app()
