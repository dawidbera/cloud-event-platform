import json
from confluent_kafka import Producer
from ..core.config import settings
from ..core.logger import get_logger
from .schemas import EventEnvelope, InventoryResultPayload

logger = get_logger(__name__)
INVENTORY_EVENTS_TOPIC = "inventory.events"
_producer = None

def get_producer() -> Producer:
    """Lazily initializes and returns a singleton instance of the Confluent Kafka Producer."""
    global _producer
    if _producer is None:
        _producer = Producer({
            'bootstrap.servers': settings.kafka_bootstrap_servers,
            'client.id': 'inventory-service',
            'acks': 'all',
        })
    return _producer

def delivery_report(err, msg):
    """Callback to log delivery success or failure for published inventory events."""
    if err is not None:
        logger.error(f"Message delivery failed: {err}")
    else:
        logger.debug(f"Message delivered to {msg.topic()} [{msg.partition()}]")

def publish_inventory_result(order_id: str, status: str, reason: str | None = None, correlation_id: str | None = None) -> None:
    """Publishes a success or failure domain event to the inventory topics detailing the result of a stock reservation attempt."""
    payload = InventoryResultPayload(order_id=order_id, status=status, reason=reason)
    event_type = "InventoryReserved" if status == "SUCCESS" else "InventoryReservationFailed"
    envelope = EventEnvelope(event_type=event_type, correlation_id=correlation_id, payload=payload.model_dump())
    
    p = get_producer()
    try:
        p.produce(
            topic=INVENTORY_EVENTS_TOPIC,
            key=order_id.encode('utf-8'),
            value=json.dumps(envelope.model_dump()).encode('utf-8'),
            callback=delivery_report
        )
        p.poll(0)
    except Exception as e:
        logger.error(f"Failed to publish inventory event: {e}")
