from pydantic import BaseModel
from typing import Optional
from datetime import datetime

#base schema for inventory
class InventoryBase(BaseModel):
    product_id: int
    quantity: int

#schema for creating or updating inventory
class InventoryUpdate(BaseModel):
    quantity: int

#schema for response
class InventoryResponse(InventoryBase):
    last_updated: datetime

    class Config:
        orm_mode = True