import redis
import logging

logger = logging.getLogger(__name__)

class IdempotencyManager:
    def __init__(self, redis_url: str):
        self.client = redis.from_url(redis_url)
        self.ttl = 86400 * 7 # 7 days TTL

    def is_processed(self, event_id: str) -> bool:
        """
        Tries to set the event_id in Redis.
        Returns True if the event was already processed (key exists),
        False if it's a new event.
        """
        key = f"idempotency:event:{event_id}"
        # setnx returns True if the key was created, False if it already existed
        is_new = self.client.set(key, "PROCESSING", nx=True, ex=self.ttl)
        if not is_new:
            logger.info(f"Event {event_id} is already processed or being processed.")
            return True
        return False

    def mark_completed(self, event_id: str):
        key = f"idempotency:event:{event_id}"
        self.client.set(key, "COMPLETED", ex=self.ttl)

    def mark_failed(self, event_id: str):
        key = f"idempotency:event:{event_id}"
        self.client.delete(key)
