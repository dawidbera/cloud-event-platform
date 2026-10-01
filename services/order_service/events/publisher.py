from ..core.kafka import publish_event
from .schemas import EventEnvelope, OrderCreatedPayload

ORDER_EVENTS_TOPIC = "orders.events"

def publish_order_created(order_id: str, customer_id: str, total_amount: float, correlation_id: str | None = None) -> None:
    """Builds an OrderCreated event envelope and publishes it to the orders.events topic to kick off downstream processes like payment."""
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

def publish_inventory_reservation_requested(order_id: str, correlation_id: str | None = None) -> None:
    """Dispatches an InventoryReservationRequested event on the orders topic to secure stock for a newly created order."""
    # Just passing order_id in the payload
    envelope = EventEnvelope(
        event_type="InventoryReservationRequested",
        correlation_id=correlation_id,
        payload={"order_id": order_id}
    )
    
    publish_event(
        topic=ORDER_EVENTS_TOPIC,
        key=order_id,
        value=envelope.model_dump()
    )
