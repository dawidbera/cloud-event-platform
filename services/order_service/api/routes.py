import uuid
from typing import Any
from fastapi import APIRouter, status, Request, Depends
from sqlalchemy.orm import Session
from .models import OrderCreateRequest, OrderResponse, OrderItem as APIOrderItem
from ..core.exceptions import OrderNotFoundException
from ..core.database import get_db
from ..models.domain import Order, OrderItem
from ..events.publisher import publish_order_created

router = APIRouter()

@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> dict[str, str]:
    """Basic liveness probe endpoint used by Kubernetes to verify the service is running."""
    return {"status": "ok"}

@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness_check(db: Session = Depends(get_db)) -> dict[str, str]:
    """Readiness probe endpoint that verifies active connections to the database and external dependencies."""
    # Check DB connectivity
    from sqlalchemy import text
    db.execute(text("SELECT 1"))
    # TODO: Add logic to check Redis and Kafka connectivity
    return {"status": "ready"}

@router.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(request: Request, order_req: OrderCreateRequest, db: Session = Depends(get_db)) -> OrderResponse:
    """Handles the creation of a new order, saving it to the database and publishing an OrderCreated event to Kafka."""
    total_amount = sum(item.price * item.quantity for item in order_req.items)
    
    order = Order(
        customer_id=order_req.customer_id,
        status="CREATED",
        total_amount=total_amount
    )
    db.add(order)
    db.flush() # flush to get order.id

    for item_req in order_req.items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item_req.product_id,
            quantity=item_req.quantity,
            price=item_req.price
        )
        db.add(order_item)

    db.commit()
    db.refresh(order)
    
    # Publish OrderCreated event to Kafka
    correlation_id = getattr(request.state, "correlation_id", None)
    publish_order_created(
        order_id=str(order.id),
        customer_id=order.customer_id,
        total_amount=order.total_amount,
        correlation_id=correlation_id
    )
    
    order.status = "PAYMENT_PENDING"
    db.commit()
    
    api_items = [
        APIOrderItem(product_id=i.product_id, quantity=i.quantity, price=i.price)
        for i in order.items
    ]
    
    return OrderResponse(
        id=order.id,
        customer_id=order.customer_id,
        status=order.status,
        total_amount=order.total_amount,
        items=api_items
    )

@router.get("/orders/{order_id}", response_model=OrderResponse, status_code=status.HTTP_200_OK)
async def get_order(order_id: str, db: Session = Depends(get_db)) -> OrderResponse:
    """Retrieves a specific order by its unique identifier, raising an exception if the order does not exist."""
    try:
        order_uuid = uuid.UUID(order_id)
    except ValueError:
        raise OrderNotFoundException(order_id=order_id)
        
    order = db.query(Order).filter(Order.id == order_uuid).first()
    if not order:
        raise OrderNotFoundException(order_id=order_id)
        
    api_items = [
        APIOrderItem(product_id=i.product_id, quantity=i.quantity, price=i.price)
        for i in order.items
    ]

    return OrderResponse(
        id=order.id,
        customer_id=order.customer_id,
        status=order.status,
        total_amount=order.total_amount,
        items=api_items
    )
