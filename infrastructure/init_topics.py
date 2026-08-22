import logging
from confluent_kafka.admin import AdminClient, NewTopic
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_topics(bootstrap_servers: str):
    admin = AdminClient({'bootstrap.servers': bootstrap_servers})
    
    # Define topics based on conventions (e.g. 3 partitions, RF 1 for local)
    topic_configs = [
        NewTopic("orders.events", num_partitions=3, replication_factor=1),
        NewTopic("orders.events.dlq", num_partitions=3, replication_factor=1),
        NewTopic("payments.events", num_partitions=3, replication_factor=1),
        NewTopic("payments.events.dlq", num_partitions=3, replication_factor=1),
        NewTopic("inventory.events", num_partitions=3, replication_factor=1),
        NewTopic("inventory.events.dlq", num_partitions=3, replication_factor=1)
    ]
    
    # Retry loop in case Kafka is not ready
    max_retries = 10
    for i in range(max_retries):
        try:
            # Wait for broker
            metadata = admin.list_topics(timeout=5)
            existing_topics = set(metadata.topics.keys())
            
            topics_to_create = [t for t in topic_configs if t.topic not in existing_topics]
            if not topics_to_create:
                logger.info("All topics already exist.")
                return
                
            fs = admin.create_topics(topics_to_create)
            for topic, f in fs.items():
                try:
                    f.result()  # The result itself is None
                    logger.info(f"Topic {topic} created")
                except Exception as e:
                    logger.error(f"Failed to create topic {topic}: {e}")
            return
        except Exception as e:
            logger.warning(f"Kafka not ready, retrying ({i+1}/{max_retries}): {e}")
            time.sleep(3)
            
    logger.error("Failed to initialize Kafka topics.")

if __name__ == "__main__":
    init_topics("localhost:9092")
