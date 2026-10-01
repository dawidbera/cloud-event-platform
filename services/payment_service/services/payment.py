import uuid
import random
import time
from ..core.logger import get_logger
from ..events.publisher import publish_payment_result

logger = get_logger(__name__)

def process_payment(order_id: str, amount: float, correlation_id: str | None = None) -> None:
    """Simulates communicating with a payment gateway, artificially failing transactions over 10k or randomly at 10%, then publishes the outcome."""
    logger.info(f"[{correlation_id}] Processing payment for order {order_id} (Amount: {amount})")
    
    # Simulate processing delay
    time.sleep(random.uniform(0.1, 0.5))
    
    payment_id = str(uuid.uuid4())
    
    # Simulate controlled failure for testing (e.g., 10% chance of failure)
    # Alternatively, you could fail based on amount (e.g., amount > 1000)
    if amount > 10000.0 or random.random() < 0.1:
        logger.warning(f"[{correlation_id}] Payment failed for order {order_id}")
        publish_payment_result(
            order_id=order_id,
            payment_id=payment_id,
            status="FAILED",
            reason="Insufficient funds or limit exceeded",
            correlation_id=correlation_id
        )
    else:
        logger.info(f"[{correlation_id}] Payment successful for order {order_id}")
        publish_payment_result(
            order_id=order_id,
            payment_id=payment_id,
            status="SUCCESS",
            correlation_id=correlation_id
        )
