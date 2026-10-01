import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid

# Set env vars to avoid parsing issues
import os
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from services.order_service.core.database import Base, SessionLocal, engine
from services.order_service.models.order import Order, OrderItem
from services.order_service.services.state_machine import handle_payment_event, handle_inventory_event

# Recreate DB for tests
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def create_test_order(db):
    order_id = str(uuid.uuid4())
    order = Order(
        id=order_id,
        customer_id="cust-123",
        total_amount=200.0,
        status="PAYMENT_PENDING"
    )
    db.add(order)
    db.commit()
    return order_id

def test_successful_order_processing():
    """
    Tests the happy path:
    1. Order created (PAYMENT_PENDING)
    2. Payment Completed -> INVENTORY_RESERVED (wait, does payment trigger inventory, or do they happen in parallel?)
    Let's check what state machine does.
    """
    db = TestingSessionLocal()
    order_id = create_test_order(db)
    
    # 1. Simulate PaymentCompleted event
    handle_payment_event({"order_id": order_id, "status": "SUCCESS"}, "PaymentCompleted")
    
    # Verify state after payment
    db.expire_all()
    order_after_payment = db.query(Order).filter(Order.id == order_id).first()
    # It should transition to either PAYMENT_COMPLETED or INVENTORY_PENDING
    assert order_after_payment.status in ["PAYMENT_COMPLETED", "INVENTORY_RESERVED", "COMPLETED"]
    
    # 2. Simulate InventoryReserved event
    handle_inventory_event({"order_id": order_id, "status": "SUCCESS"}, "InventoryReserved")
    
    # Verify final state
    db.expire_all()
    order_final = db.query(Order).filter(Order.id == order_id).first()
    assert order_final.status == "COMPLETED"

def test_payment_failed_processing():
    db = TestingSessionLocal()
    order_id = create_test_order(db)
    
    # Simulate PaymentFailed event
    handle_payment_event({"order_id": order_id, "reason": "Insufficient funds"}, "PaymentFailed")
    
    db.expire_all()
    order_failed = db.query(Order).filter(Order.id == order_id).first()
    assert order_failed.status == "FAILED"

def test_inventory_failed_processing():
    db = TestingSessionLocal()
    order_id = create_test_order(db)
    
    # Simulate Payment success first
    handle_payment_event({"order_id": order_id, "status": "SUCCESS"}, "PaymentCompleted")
    
    # Simulate InventoryReservationFailed
    handle_inventory_event({"order_id": order_id, "reason": "Out of stock"}, "InventoryReservationFailed")
    
    db.expire_all()
    order_failed = db.query(Order).filter(Order.id == order_id).first()
    assert order_failed.status == "FAILED"
