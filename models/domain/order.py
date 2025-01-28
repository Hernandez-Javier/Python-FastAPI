from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from db.session import Base

class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, default="pending")
    total_amount = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)