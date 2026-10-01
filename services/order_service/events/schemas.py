from pydantic import BaseModel, Field
from datetime import datetime, timezone
import uuid
from typing import Any, Dict

class EventEnvelope(BaseModel):
    """Standardized wrapper for all outgoing events, providing metadata like event ID, type, and timestamp, along with the domain-specific payload."""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str
    event_version: str = "v1"
    correlation_id: str | None = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    payload: Dict[str, Any]

class OrderCreatedPayload(BaseModel):
    """Payload schema for the OrderCreated event, containing essential order details like ID, customer, and total amount."""
    order_id: str
    customer_id: str
    total_amount: float
