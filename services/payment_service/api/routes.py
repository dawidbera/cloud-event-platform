from fastapi import APIRouter, status

router = APIRouter()

@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> dict[str, str]:
    """Exposes a lightweight health check endpoint to verify the service is running and responsive."""
    return {"status": "ok"}

@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness_check() -> dict[str, str]:
    """Verifies the service is fully operational and ready to process incoming HTTP requests."""
    # In a real scenario, check if consumer is alive/connected
    return {"status": "ready"}
