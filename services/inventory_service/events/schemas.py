from pydantic import BaseModel, Field
from datetime import datetime, timezone
import uuid
from typing import Any, Dict, List

class EventEnvelope(BaseModel):
    """Standardized wrapper for domain events providing common metadata like event ID, type, correlation ID, and timestamps."""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str
    event_version: str = "v1"
    correlation_id: str | None = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    payload: Dict[str, Any]

class InventoryResultPayload(BaseModel):
    """The specific data payload for inventory outcome events, recording the order affected, the final status, and failure reasons if any."""
    order_id: str
    status: str
    reason: str | None = None
