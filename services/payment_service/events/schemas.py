from pydantic import BaseModel, Field
from datetime import datetime, timezone
import uuid
from typing import Any, Dict

class EventEnvelope(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str
    event_version: str = "v1"
    correlation_id: str | None = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    payload: Dict[str, Any]

class PaymentResultPayload(BaseModel):
    order_id: str
    payment_id: str
    status: str  # SUCCESS or FAILED
    reason: str | None = None
