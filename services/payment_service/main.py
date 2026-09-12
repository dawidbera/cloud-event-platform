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
    # Startup
    consumer_thread.start()
    yield
    # Shutdown
    consumer_thread.stop()
    consumer_thread.join(timeout=5.0)

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan
    )
    
    app.include_router(api_router)
    return app

app = create_app()
