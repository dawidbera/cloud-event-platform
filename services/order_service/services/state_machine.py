import logging
from sqlalchemy.orm import Session
from ..models.domain import Order
from ..core.database import SessionLocal
from ..events.publisher import publish_inventory_reservation_requested

logger = logging.getLogger(__name__)

# Valid transitions
# CREATED -> PAYMENT_PENDING (Initial creation triggers this, or just stays CREATED until payment)
# PAYMENT_PENDING -> PAYMENT_COMPLETED, PAYMENT_FAILED
# PAYMENT_COMPLETED -> INVENTORY_RESERVED, INVENTORY_FAILED
# INVENTORY_RESERVED -> COMPLETED

def update_order_status(order_id: str, new_event: str):
    """Retrieves an order and applies state transitions based on external domain events, potentially emitting new events in response."""
    with SessionLocal() as db:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            logger.error(f"Order {order_id} not found for state update.")
            return

        current_status = order.status
        new_status = current_status
        should_publish_inventory = False

        if new_event == "PaymentCompleted":
            if current_status in ["CREATED", "PAYMENT_PENDING"]:
                new_status = "PAYMENT_COMPLETED"
                should_publish_inventory = True
                
        elif new_event == "InventoryReserved":
            if current_status == "PAYMENT_COMPLETED":
                new_status = "COMPLETED"
                
        elif new_event == "PaymentFailed":
            if current_status in ["CREATED", "PAYMENT_PENDING"]:
                new_status = "PAYMENT_FAILED"
            
        elif new_event == "InventoryReservationFailed":
            if current_status == "PAYMENT_COMPLETED":
                new_status = "INVENTORY_FAILED"

        if new_status != current_status:
            logger.info(f"Order {order_id} transition: {current_status} -> {new_status}")
            order.status = new_status
            db.commit()
            
            # Publish event if needed
            if should_publish_inventory:
                publish_inventory_reservation_requested(order_id)
        else:
            logger.debug(f"Order {order_id} state unchanged from {current_status} on {new_event}")

def handle_payment_event(payload: dict, event_type: str):
    """Extracts the order ID from a payment event payload and routes it to the state machine for processing."""
    order_id = payload.get("order_id")
    update_order_status(order_id, event_type)

def handle_inventory_event(payload: dict, event_type: str):
    """Extracts the order ID from an inventory event payload and routes it to the state machine for processing."""
    order_id = payload.get("order_id")
    update_order_status(order_id, event_type)
