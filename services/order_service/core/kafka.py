import json
import logging
from confluent_kafka import Producer
from .config import settings

logger = logging.getLogger(__name__)

_producer = None

def get_producer() -> Producer:
    global _producer
    if _producer is None:
        producer_config = {
            'bootstrap.servers': settings.kafka_bootstrap_servers,
            'client.id': 'order-service',
            'acks': 'all',
        }
        _producer = Producer(producer_config)
    return _producer

def delivery_report(err, msg):
    if err is not None:
        logger.error(f"Message delivery failed: {err}")
    else:
        logger.debug(f"Message delivered to {msg.topic()} [{msg.partition()}]")

def publish_event(topic: str, key: str, value: dict):
    p = get_producer()
    try:
        p.produce(
            topic=topic,
            key=key.encode('utf-8'),
            value=json.dumps(value).encode('utf-8'),
            callback=delivery_report
        )
        p.poll(0)
    except Exception as e:
        logger.error(f"Failed to publish event to {topic}: {e}")
