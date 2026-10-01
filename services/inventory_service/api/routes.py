from fastapi import APIRouter, status

router = APIRouter()

@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> dict[str, str]:
    """Returns a basic 200 OK health status, used by load balancers and container orchestrators for liveness checks."""
    return {"status": "ok"}

@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness_check() -> dict[str, str]:
    """Confirms the service is fully booted and ready to receive traffic."""
    return {"status": "ready"}
