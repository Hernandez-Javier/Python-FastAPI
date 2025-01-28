from pydantic import BaseModel

class OrderItemBase(BaseModel):
    order_id: int
    product_id: int
    quantity: int
    price: float

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemResponse(OrderItemBase):
    order_id: int
    product_id: int
    quantity: int
    price: float

    class Config:
        from_attributes = True