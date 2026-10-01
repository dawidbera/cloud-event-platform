import json
import threading
from confluent_kafka import Consumer, KafkaError
from ..core.config import settings
from ..services.state_machine import handle_payment_event, handle_inventory_event
from shared.kafka.idempotency import IdempotencyManager
import logging
import time
from shared.observability.metrics import EVENTS_PROCESSED, EVENTS_FAILED, EVENT_PROCESSING_LATENCY

logger = logging.getLogger(__name__)

class OrderEventConsumer(threading.Thread):
    """Background thread consumer that listens to payment and inventory Kafka topics, handling incoming events idempotently."""
    def __init__(self):
        """Initializes the Kafka consumer with bootstrap servers and group ID, and sets up the idempotency manager."""
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
        """Main event loop for the consumer thread. Continuously polls Kafka, checks idempotency, and routes events to their handlers."""
        self._running = True
        self._consumer.subscribe(["payments.events", "inventory.events"])
        logger.info("OrderEventConsumer subscribed to payments.events and inventory.events")
        
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
                    event_type = value.get("event_type")
                    event_id = value.get("event_id")
                    payload = value.get("payload", {})
                    
                    if event_id and self.idempotency.is_processed(event_id):
                        continue
                    
                    if event_type in ["PaymentCompleted", "PaymentFailed"]:
                        start_time = time.time()
                        handle_payment_event(payload, event_type)
                        EVENT_PROCESSING_LATENCY.labels(event_type=event_type, service="order_service").observe(time.time() - start_time)
                        EVENTS_PROCESSED.labels(event_type=event_type, service="order_service").inc()
                    elif event_type in ["InventoryReserved", "InventoryReservationFailed"]:
                        start_time = time.time()
                        handle_inventory_event(payload, event_type)
                        EVENT_PROCESSING_LATENCY.labels(event_type=event_type, service="order_service").observe(time.time() - start_time)
                        EVENTS_PROCESSED.labels(event_type=event_type, service="order_service").inc()
                        
                    if event_id:
                        self.idempotency.mark_completed(event_id)
                except Exception as e:
                    logger.error(f"Error processing message in OrderEventConsumer: {e}")
                    if 'event_type' in locals():
                        EVENTS_FAILED.labels(event_type=event_type, service="order_service").inc()
                    if 'event_id' in locals() and event_id:
                        self.idempotency.mark_failed(event_id)
        finally:
            self._consumer.close()
            logger.info("OrderEventConsumer closed.")

    def stop(self):
        """Signals the consumer thread to stop processing and exit gracefully."""
        self._running = False
