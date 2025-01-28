import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from db.session import get_db
from models.domain.product import Product
from typing import List
from datetime import datetime
from models.domain.inventory import Inventory
from models.domain.order import Order
from models.domain.orderItem import OrderItem
from slowapi import Limiter
from slowapi.util import get_remote_address

#configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

router = APIRouter()

#Create Limiter instance
limiter = Limiter(key_func=get_remote_address)

#Get low stock inventory, 5 is considered low
@router.get("/reports/low-stock", response_model=List[dict])
@limiter.limit("5/minute")  #Limit: 5 requests per minute for low-stock report
def get_low_stock(request: Request, threshold: int = 5, db: Session = Depends(get_db)):
    logger.info(f"Fetching low stock inventory with threshold: {threshold}")
    
    low_stock_items = (
        db.query(Inventory, Product.name)
        .join(Product, Inventory.product_id == Product.id)
        .filter(Inventory.quantity < threshold)
        .all()
    )

    logger.info(f"Found {len(low_stock_items)} low stock items")

    #Return results in a readable format
    return [
        {
            "id": item.Inventory.product_id,
            "name": item.name,
            "stock": item.Inventory.quantity,
            "last_updated": item.Inventory.last_updated
        }
        for item in low_stock_items
    ]

#get report of sales
@router.get("/reports/sales", response_model=List[dict])
@limiter.limit("5/minute")  #limit: 5 requests per minute for sales report
def get_sales_report(request: Request, start_date: datetime, end_date: datetime, db: Session = Depends(get_db)):
    logger.info(f"Fetching sales report from {start_date} to {end_date}")
    
    sales_data = (
        db.query(
            OrderItem.product_id,
            func.sum(OrderItem.quantity).label("total_quantity"),
            func.sum(OrderItem.price * OrderItem.quantity).label("total_sales")
        )
        .join(Order, Order.id == OrderItem.order_id)
        .filter(Order.created_at.between(start_date, end_date))
        .group_by(OrderItem.product_id)
        .all()
    )
    
    logger.info(f"Sales report generated with {len(sales_data)} products")

    return [
        {"product_id": item.product_id, "total_quantity": item.total_quantity, "total_sales": item.total_sales}
        for item in sales_data
    ]