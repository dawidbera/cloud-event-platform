import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware that extracts or generates a unique correlation ID for each request to enable distributed tracing."""
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Intercepts the incoming request to inject a correlation ID into the application state and response headers."""
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        request.state.correlation_id = correlation_id
        
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        
        return response
