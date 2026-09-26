import json
import threading
from confluent_kafka import Consumer, KafkaError
from ..core.config import settings
from ..services.state_machine import handle_payment_event, handle_inventory_event
import logging

logger = logging.getLogger(__name__)

class OrderEventConsumer(threading.Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True
        self._running = False
        self._consumer = Consumer({
            'bootstrap.servers': settings.kafka_bootstrap_servers,
            'group.id': settings.consumer_group_id,
            'auto.offset.reset': 'earliest'
        })
        
    def run(self):
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
                    payload = value.get("payload", {})
                    
                    if event_type in ["PaymentCompleted", "PaymentFailed"]:
                        handle_payment_event(payload, event_type)
                    elif event_type in ["InventoryReserved", "InventoryReservationFailed"]:
                        handle_inventory_event(payload, event_type)
                except Exception as e:
                    logger.error(f"Error processing message in OrderEventConsumer: {e}")
        finally:
            self._consumer.close()
            logger.info("OrderEventConsumer closed.")

    def stop(self):
        self._running = False
