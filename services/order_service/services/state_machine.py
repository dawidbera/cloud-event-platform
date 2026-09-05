import logging
from sqlalchemy.orm import Session
from ..models.domain import Order
from ..core.database import SessionLocal

logger = logging.getLogger(__name__)

# Valid transitions
# CREATED -> PAYMENT_COMPLETED, INVENTORY_RESERVED, PAYMENT_FAILED, INVENTORY_FAILED
# PAYMENT_COMPLETED -> COMPLETED, INVENTORY_FAILED
# INVENTORY_RESERVED -> COMPLETED, PAYMENT_FAILED

def update_order_status(order_id: str, new_event: str):
    with SessionLocal() as db:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            logger.error(f"Order {order_id} not found for state update.")
            return

        current_status = order.status
        new_status = current_status

        if new_event == "PaymentCompleted":
            if current_status == "CREATED":
                new_status = "PAYMENT_COMPLETED"
            elif current_status == "INVENTORY_RESERVED":
                new_status = "COMPLETED"
                
        elif new_event == "InventoryReserved":
            if current_status == "CREATED":
                new_status = "INVENTORY_RESERVED"
            elif current_status == "PAYMENT_COMPLETED":
                new_status = "COMPLETED"
                
        elif new_event == "PaymentFailed":
            new_status = "PAYMENT_FAILED"
            
        elif new_event == "InventoryReservationFailed":
            new_status = "INVENTORY_FAILED"

        if new_status != current_status:
            logger.info(f"Order {order_id} transition: {current_status} -> {new_status}")
            order.status = new_status
            db.commit()
        else:
            logger.debug(f"Order {order_id} state unchanged from {current_status} on {new_event}")

def handle_payment_event(payload: dict):
    order_id = payload.get("order_id")
    status = payload.get("status")
    
    if status == "SUCCESS":
        update_order_status(order_id, "PaymentCompleted")
    else:
        update_order_status(order_id, "PaymentFailed")

def handle_inventory_event(payload: dict):
    order_id = payload.get("order_id")
    status = payload.get("status")
    
    if status == "SUCCESS":
        update_order_status(order_id, "InventoryReserved")
    else:
        update_order_status(order_id, "InventoryReservationFailed")
