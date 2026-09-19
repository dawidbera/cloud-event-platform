import json
import threading
from confluent_kafka import Consumer, KafkaError
from ..core.config import settings
from ..core.logger import get_logger
from ..services.inventory import reserve_inventory

logger = get_logger(__name__)
ORDER_EVENTS_TOPIC = "orders.events"

class InventoryEventConsumer(threading.Thread):
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
                    if value.get("event_type") == "OrderCreated":
                        order_id = value.get("payload", {}).get("order_id")
                        if order_id:
                            reserve_inventory(order_id, value.get("correlation_id"))
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
        finally:
            self._consumer.close()
            logger.info("Inventory consumer closed.")

    def stop(self):
        self._running = False
