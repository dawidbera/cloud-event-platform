from ..core.kafka import publish_event
from .schemas import EventEnvelope, OrderCreatedPayload

ORDER_EVENTS_TOPIC = "orders.events"

def publish_order_created(order_id: str, customer_id: str, total_amount: float, correlation_id: str | None = None) -> None:
    payload = OrderCreatedPayload(
        order_id=order_id,
        customer_id=customer_id,
        total_amount=total_amount
    )
    
    envelope = EventEnvelope(
        event_type="OrderCreated",
        correlation_id=correlation_id,
        payload=payload.model_dump()
    )
    
    publish_event(
        topic=ORDER_EVENTS_TOPIC,
        key=order_id,
        value=envelope.model_dump()
    )
