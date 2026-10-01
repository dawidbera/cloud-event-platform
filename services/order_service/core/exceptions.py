from fastapi import Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    """Standardized API response schema for returning error details and correlation IDs to the client."""
    message: str
    error_code: str
    correlation_id: str | None = None

class OrderNotFoundException(Exception):
    """Custom exception raised when an requested order cannot be found in the database."""
    def __init__(self, order_id: str):
        """Initializes the exception with the specific order ID that could not be located."""
        self.order_id = order_id
        self.message = f"Order with ID {order_id} not found."
        super().__init__(self.message)

async def order_not_found_handler(request: Request, exc: OrderNotFoundException) -> JSONResponse:
    """FastAPI exception handler that catches OrderNotFoundException and returns a formatted HTTP 404 response."""
    correlation_id = getattr(request.state, "correlation_id", None)
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=ErrorResponse(
            message=exc.message,
            error_code="ORDER_NOT_FOUND",
            correlation_id=correlation_id
        ).model_dump()
    )

async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Fallback exception handler that catches unexpected errors and returns a generic HTTP 500 response to prevent leaking internal details."""
    correlation_id = getattr(request.state, "correlation_id", None)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            message="Internal server error occurred.",
            error_code="INTERNAL_SERVER_ERROR",
            correlation_id=correlation_id
        ).model_dump()
    )
