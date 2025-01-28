from pydantic import BaseModel
from datetime import datetime
from typing import List

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int
    price: float

class OrderBase(BaseModel):
    status: str
    total_amount: float

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

    class Config:
        orm_mode = True

class OrderResponse(OrderBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True