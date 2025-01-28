import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from models.domain.order import Order
from models.domain.orderItem import OrderItem
from schemas.order import OrderCreate, OrderResponse
from db.session import get_db
from typing import List
from slowapi import Limiter
from slowapi.util import get_remote_address

#Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

router = APIRouter()

#Create Limiter instance
limiter = Limiter(key_func=get_remote_address)

#Create a new order
@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")  #Limit: 5 requests per minute
def create_order(request: Request, order: OrderCreate, db: Session = Depends(get_db)):
    logger.info(f"Received request to create order with total amount: {order.total_amount}, status: {order.status}")
    
    db_order = Order(
        status=order.status,
        total_amount=order.total_amount
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    logger.info(f"Order created successfully with ID: {db_order.id}")
    
    #create order items for the order
    for item in order.items:
        db_item = OrderItem(
            order_id=db_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.price
        )
        db.add(db_item)
    
    db.commit()
    logger.info(f"Order items for order ID {db_order.id} created successfully")
    return db_order

#Get all order records
@router.get("/", response_model=List[OrderResponse])
@limiter.limit("5/minute")  #Limit: 5 requests per minute
def get_orders(request: Request, db: Session = Depends(get_db)):
    logger.info("Fetching all orders")
    orders = db.query(Order).all()
    logger.info(f"Found {len(orders)} orders")
    return orders

#Get order by ID
@router.get("/{order_id}", response_model=OrderResponse)
@limiter.limit("5/minute")  #limit: 5 requests per minute
def get_order(order_id: int, request: Request, db: Session = Depends(get_db)):
    logger.info(f"Fetching order with ID: {order_id}")
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        logger.warning(f"Order with ID {order_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    #Get order items
    order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
    order.items = order_items
    logger.info(f"Found order with ID {order_id} and {len(order.items)} items")
    return order

#Update order status
@router.put("/{order_id}/status", response_model=OrderResponse)
@limiter.limit("3/minute")  #Limit: 3 requests per minute for updating order status
def update_order_status(request: Request, order_id: int, status: str, db: Session = Depends(get_db)):
    logger.info(f"Updating status for order ID {order_id} to {status}")
    
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        logger.warning(f"Order with ID {order_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    db_order.status = status
    db.commit()
    db.refresh(db_order)
    
    logger.info(f"Order ID {order_id} status updated to {status}")
    return db_order