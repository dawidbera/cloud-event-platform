from fastapi import Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    message: str
    error_code: str
    correlation_id: str | None = None

class OrderNotFoundException(Exception):
    def __init__(self, order_id: str):
        self.order_id = order_id
        self.message = f"Order with ID {order_id} not found."
        super().__init__(self.message)

async def order_not_found_handler(request: Request, exc: OrderNotFoundException) -> JSONResponse:
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
    correlation_id = getattr(request.state, "correlation_id", None)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            message="Internal server error occurred.",
            error_code="INTERNAL_SERVER_ERROR",
            correlation_id=correlation_id
        ).model_dump()
    )
