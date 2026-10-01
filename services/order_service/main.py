import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from .core.config import settings
from .core.middleware import CorrelationIdMiddleware
from .core.exceptions import OrderNotFoundException, order_not_found_handler, global_exception_handler
from .api.routes import router as api_router
from .events.consumer import OrderEventConsumer

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan context manager handling startup routines like launching the background Kafka consumer and ensuring graceful shutdown."""
    # Startup
    consumer = OrderEventConsumer()
    consumer.start()
    logger.info("Order service started")
    yield
    # Shutdown
    consumer.stop()
    consumer.join()
    logger.info("Order service stopped")

def create_app() -> FastAPI:
    """Factory function that instantiates the FastAPI application, configuring middleware, exception handlers, routing, and observability tooling."""
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan
    )
    
    # Middleware
    app.add_middleware(CorrelationIdMiddleware)
    
    # Exception Handlers
    app.add_exception_handler(OrderNotFoundException, order_not_found_handler)
    app.add_exception_handler(Exception, global_exception_handler)
    
    # Routers
    app.include_router(api_router)
    
    # Prometheus Metrics
    try:
        from prometheus_fastapi_instrumentator import Instrumentator
        Instrumentator().instrument(app).expose(app)
    except ImportError:
        logger.warning("prometheus-fastapi-instrumentator not installed, /metrics endpoint disabled")
        
    # OpenTelemetry Tracing
    try:
        from shared.observability.tracing import setup_tracing
        setup_tracing(app, "order_service")
    except Exception as e:
        logger.warning(f"Failed to setup tracing: {e}")
    
    return app

app = create_app()
