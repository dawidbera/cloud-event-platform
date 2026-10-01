from pydantic import BaseModel, Field
from typing import List
from uuid import UUID

class OrderItem(BaseModel):
    """API schema representing a single product line item within an order, including quantity and price."""
    product_id: str = Field(..., description="ID of the product")
    quantity: int = Field(..., gt=0, description="Quantity of the product")
    price: float = Field(..., gt=0.0, description="Price per unit")

class OrderCreateRequest(BaseModel):
    """API schema for the incoming request to create a new order, containing the customer ID and a list of items."""
    customer_id: str = Field(..., description="ID of the customer")
    items: List[OrderItem] = Field(..., min_length=1, description="List of items in the order")

class OrderResponse(BaseModel):
    """API schema for the outgoing response detailing an order, including its generated ID, status, and calculated total."""
    id: UUID
    customer_id: str
    status: str
    total_amount: float
    items: List[OrderItem]
