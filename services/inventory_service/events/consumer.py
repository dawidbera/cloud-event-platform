import json
import threading
from confluent_kafka import Consumer, KafkaError
from ..core.config import settings
from ..core.logger import get_logger
from ..services.inventory import reserve_inventory

from shared.kafka.idempotency import IdempotencyManager

logger = get_logger(__name__)
ORDER_EVENTS_TOPIC = "orders.events"

class InventoryEventConsumer(threading.Thread):
    """Consumes Kafka events on the orders topic to process inventory reservation requests."""
    def __init__(self):
        """Initializes the Kafka consumer, connects to Redis for idempotency tracking, and prepares the background thread."""
        super().__init__()
        self.daemon = True
        self._running = False
        self.idempotency = IdempotencyManager(settings.redis_url)
        self._consumer = Consumer({
            'bootstrap.servers': settings.kafka_bootstrap_servers,
            'group.id': settings.consumer_group_id,
            'auto.offset.reset': 'earliest'
        })
        
    def run(self):
        """Continuously polls the Kafka topic for new messages, filters out already-processed events to maintain idempotency, and triggers the reservation process."""
        self._running = True
        self._consumer.subscribe([ORDER_EVENTS_TOPIC])
        logger.info(f"Subscribed to {ORDER_EVENTS_TOPIC}")
        
        try:
            while self._running:
                msg = self._consumer.poll(timeout=1.0)
                if msg is None: continue
                if msg.error():
                    if msg.error().code() != KafkaError._PARTITION_EOF:
                        logger.error(f"Consumer error: {msg.error()}")
                        break
                    continue
                
                try:
                    value = json.loads(msg.value().decode('utf-8'))
                    event_id = value.get("event_id")
                    
                    if event_id and self.idempotency.is_processed(event_id):
                        continue
                        
                    if value.get("event_type") == "InventoryReservationRequested":
                        order_id = value.get("payload", {}).get("order_id")
                        if order_id:
                            reserve_inventory(order_id, value.get("correlation_id"))
                            
                    if event_id:
                        self.idempotency.mark_completed(event_id)
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    if 'event_id' in locals() and event_id:
                        self.idempotency.mark_failed(event_id)
        finally:
            self._consumer.close()
            logger.info("Inventory consumer closed.")

    def stop(self):
        """Signals the consumer thread to stop polling and gracefully shut down."""
        self._running = False
