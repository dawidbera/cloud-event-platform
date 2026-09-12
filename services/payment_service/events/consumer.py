import json
import threading
from confluent_kafka import Consumer, KafkaError, KafkaException
from ..core.config import settings
from ..core.logger import get_logger
from ..services.payment import process_payment

logger = get_logger(__name__)

ORDER_EVENTS_TOPIC = "orders.events"

class PaymentEventConsumer(threading.Thread):
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
        logger.info(f"Subscribed to {ORDER_EVENTS_TOPIC}. Starting consumer loop.")
        
        try:
            while self._running:
                msg = self._consumer.poll(timeout=1.0)
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        logger.error(f"Consumer error: {msg.error()}")
                        break
                
                self._handle_message(msg)
        finally:
            self._consumer.close()
            logger.info("Consumer closed.")

    def stop(self):
        self._running = False

    def _handle_message(self, msg):
        try:
            value = json.loads(msg.value().decode('utf-8'))
            event_type = value.get("event_type")
            correlation_id = value.get("correlation_id")
            
            if event_type == "OrderCreated":
                payload = value.get("payload", {})
                order_id = payload.get("order_id")
                amount = payload.get("total_amount")
                
                if order_id and amount is not None:
                    process_payment(order_id, amount, correlation_id)
                else:
                    logger.warning(f"[{correlation_id}] Invalid OrderCreated payload")
        except Exception as e:
            logger.error(f"Error handling message: {e}")
