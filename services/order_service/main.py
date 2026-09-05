from fastapi import FastAPI
from .core.config import settings
from .core.middleware import CorrelationIdMiddleware
from .core.exceptions import OrderNotFoundException, order_not_found_handler, global_exception_handler
from .api.routes import router as api_router

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
    )
    
    # Middleware
    app.add_middleware(CorrelationIdMiddleware)
    
    # Exception Handlers
    app.add_exception_handler(OrderNotFoundException, order_not_found_handler)
    app.add_exception_handler(Exception, global_exception_handler)
    
    # Routers
    app.include_router(api_router)
    
    return app

app = create_app()
