import random
import time
from ..core.logger import get_logger
from ..events.publisher import publish_inventory_result

logger = get_logger(__name__)

def reserve_inventory(order_id: str, correlation_id: str | None = None) -> None:
    """Simulates an inventory check and reservation, randomly failing 5% of requests to mimic out-of-stock scenarios, then publishes a result event."""
    logger.info(f"[{correlation_id}] Checking inventory for order {order_id}")
    time.sleep(random.uniform(0.1, 0.4))
    
    # Simulate 5% out-of-stock scenario
    if random.random() < 0.05:
        logger.warning(f"[{correlation_id}] Inventory reservation failed for order {order_id} (Out of stock)")
        publish_inventory_result(order_id=order_id, status="FAILED", reason="Items out of stock", correlation_id=correlation_id)
    else:
        logger.info(f"[{correlation_id}] Inventory successfully reserved for order {order_id}")
        publish_inventory_result(order_id=order_id, status="SUCCESS", correlation_id=correlation_id)
