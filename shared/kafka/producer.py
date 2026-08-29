import json
import logging
from confluent_kafka import Producer

logger = logging.getLogger(__name__)

class EventProducer:
    def __init__(self, bootstrap_servers: str, client_id: str):
        self.producer = Producer({
            'bootstrap.servers': bootstrap_servers,
            'client.id': client_id,
            'acks': 'all',
            'enable.idempotence': True,
            'retries': 5
        })

    def _delivery_report(self, err, msg):
        if err is not None:
            logger.error(f"Message delivery failed: {err}")
        else:
            logger.debug(f"Message delivered to {msg.topic()} [{msg.partition()}]")

    def publish(self, topic: str, key: str, value: dict, headers: dict | None = None):
        try:
            self.producer.produce(
                topic=topic,
                key=key.encode('utf-8') if key else None,
                value=json.dumps(value).encode('utf-8'),
                headers=headers or {},
                callback=self._delivery_report
            )
            self.producer.poll(0)
        except Exception as e:
            logger.error(f"Failed to publish event to {topic}: {e}")
            raise

    def flush(self):
        self.producer.flush()
