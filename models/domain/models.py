from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone

Base = declarative_base()

#definig db models
class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, index=True)
    description = Column(String)
    price = Column(Float)
    sku = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    inventory = relationship("Inventory", back_populates="product", uselist=False, cascade="all, delete")
    
class Inventory(Base):
    __tablename__ = "inventory"
    
    product_id = Column(Integer, ForeignKey("products.id"), primary_key=True)
    quantity = Column(Integer)
    last_updated = Column(DateTime, default=datetime.now(timezone.utc))
    
    product = relationship("Product", back_populates="inventory")

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    status = Column(String)
    total_amount = Column(Float)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

class OrderItem(Base):
    __tablename__ = "order_items"
    
    order_id = Column(Integer, ForeignKey("orders.id"), primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), primary_key=True)
    quantity = Column(Integer)
    price = Column(Float)
    
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")

#definig relations
Product.inventory = relationship("Inventory", back_populates="product", uselist=False)
Product.order_items = relationship("OrderItem", back_populates="product")
Order.items = relationship("OrderItem", back_populates="order")
