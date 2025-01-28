from sqlalchemy import Column, Integer, ForeignKey, Float
from sqlalchemy.orm import relationship
from db.session import Base

class OrderItem(Base):
    __tablename__ = 'order_items'

    order_id = Column(Integer, ForeignKey('orders.id'), primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), primary_key=True)
    quantity = Column(Integer)
    price = Column(Float)

    order = relationship('Order')
    product = relationship('Product')
