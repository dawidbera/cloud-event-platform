from pydantic import BaseModel, Field
from typing import List
from uuid import UUID

class OrderItem(BaseModel):
    product_id: str = Field(..., description="ID of the product")
    quantity: int = Field(..., gt=0, description="Quantity of the product")
    price: float = Field(..., gt=0.0, description="Price per unit")

class OrderCreateRequest(BaseModel):
    customer_id: str = Field(..., description="ID of the customer")
    items: List[OrderItem] = Field(..., min_length=1, description="List of items in the order")

class OrderResponse(BaseModel):
    id: UUID
    customer_id: str
    status: str
    total_amount: float
    items: List[OrderItem]
