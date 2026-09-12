import json
from confluent_kafka import Producer
from ..core.config import settings
from ..core.logger import get_logger
from .schemas import EventEnvelope, PaymentResultPayload

logger = get_logger(__name__)

PAYMENTS_EVENTS_TOPIC = "payments.events"

_producer = None

def get_producer() -> Producer:
    global _producer
    if _producer is None:
        producer_config = {
            'bootstrap.servers': settings.kafka_bootstrap_servers,
            'client.id': 'payment-service',
            'acks': 'all',
        }
        _producer = Producer(producer_config)
    return _producer

def delivery_report(err, msg):
    if err is not None:
        logger.error(f"Message delivery failed: {err}")
    else:
        logger.debug(f"Message delivered to {msg.topic()} [{msg.partition()}]")

def publish_payment_result(order_id: str, payment_id: str, status: str, reason: str | None = None, correlation_id: str | None = None) -> None:
    payload = PaymentResultPayload(
        order_id=order_id,
        payment_id=payment_id,
        status=status,
        reason=reason
    )
    
    event_type = "PaymentCompleted" if status == "SUCCESS" else "PaymentFailed"
    
    envelope = EventEnvelope(
        event_type=event_type,
        correlation_id=correlation_id,
        payload=payload.model_dump()
    )
    
    p = get_producer()
    try:
        p.produce(
            topic=PAYMENTS_EVENTS_TOPIC,
            key=order_id.encode('utf-8'),
            value=json.dumps(envelope.model_dump()).encode('utf-8'),
            callback=delivery_report
        )
        p.poll(0)
    except Exception as e:
        logger.error(f"Failed to publish event: {e}")
