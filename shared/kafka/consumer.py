import json
import logging
import threading
from typing import Callable
from confluent_kafka import Consumer, KafkaError
from .idempotency import IdempotencyManager
from .producer import EventProducer

logger = logging.getLogger(__name__)

class EventConsumer(threading.Thread):
    def __init__(self, bootstrap_servers: str, group_id: str, topics: list[str],
                 handler: Callable[[dict], None], 
                 dlq_topic: str | None = None,
                 idempotency_manager: IdempotencyManager | None = None,
                 producer: EventProducer | None = None):
        super().__init__()
        self.daemon = True
        self._running = False
        self.topics = topics
        self.handler = handler
        self.dlq_topic = dlq_topic
        self.idempotency = idempotency_manager
        self.producer = producer
        
        self.consumer = Consumer({
            'bootstrap.servers': bootstrap_servers,
            'group.id': group_id,
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': False
        })

    def run(self):
        self._running = True
        self.consumer.subscribe(self.topics)
        logger.info(f"Subscribed to {self.topics}")
        
        try:
            while self._running:
                msg = self.consumer.poll(timeout=1.0)
                if msg is None: continue
                if msg.error():
                    if msg.error().code() != KafkaError._PARTITION_EOF:
                        logger.error(f"Consumer error: {msg.error()}")
                    continue
                
                self._process_message(msg)
        finally:
            self.consumer.close()
            logger.info("Consumer closed.")

    def stop(self):
        self._running = False

    def _process_message(self, msg):
        event_id = None
        try:
            value = json.loads(msg.value().decode('utf-8'))
            event_id = value.get("event_id")
            
            if self.idempotency and event_id:
                if self.idempotency.is_processed(event_id):
                    self.consumer.commit(msg)
                    return

            # Execute handler
            self.handler(value)
            
            if self.idempotency and event_id:
                self.idempotency.mark_completed(event_id)
                
            self.consumer.commit(msg)
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            if self.idempotency and event_id:
                self.idempotency.mark_failed(event_id)
                
            if self.dlq_topic and self.producer:
                logger.warning(f"Sending message to DLQ: {self.dlq_topic}")
                try:
                    self.producer.publish(
                        topic=self.dlq_topic,
                        key=msg.key().decode('utf-8') if msg.key() else None,
                        value={"error": str(e), "original_message": json.loads(msg.value().decode('utf-8'))}
                    )
                    self.consumer.commit(msg) # Commit original message since it's safely in DLQ
                except Exception as dlq_e:
                    logger.error(f"Failed to send to DLQ: {dlq_e}")
