import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from datetime import datetime
from db.session import get_db
from models.domain.inventory import Inventory
from models.domain.product import Product
from schemas.inventory import InventoryUpdate, InventoryResponse
from slowapi import Limiter
from slowapi.util import get_remote_address

#Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

router = APIRouter()

#create Limiter instance
limiter = Limiter(key_func=get_remote_address)

#Apply rate limit to all inventory routes
#get all inventory records
@router.get("/", response_model=list[InventoryResponse])
@limiter.limit("5/minute")  # Limit: 5 requests per minute
def get_inventory(request: Request, db: Session = Depends(get_db)):
    logger.info("Fetching all inventory records")
    inventory = db.query(Inventory).all()
    logger.info(f"Found {len(inventory)} inventory records")
    return inventory

#get inventory entry by id
@router.get("/{product_id}", response_model=InventoryResponse)
@limiter.limit("5/minute")  #Limit: 5 requests per minute
def get_inventory_by_product(product_id: int, request: Request, db: Session = Depends(get_db)):
    logger.info(f"Fetching inventory for product ID: {product_id}")
    inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
    if not inventory:
        logger.warning(f"Inventory record not found for product ID: {product_id}")
        raise HTTPException(status_code=404, detail="Inventory record not found")
    logger.info(f"Found inventory for product ID: {product_id}, quantity: {inventory.quantity}")
    return inventory

#modify an inventory entry
@router.put("/{product_id}", response_model=InventoryResponse)
@limiter.limit("3/minute")  #Limit: 3 requests per minute for updating inventory
def update_inventory(product_id: int, inventory_data: InventoryUpdate, request: Request, db: Session = Depends(get_db)):
    logger.info(f"Updating inventory for product ID: {product_id} with new quantity: {inventory_data.quantity}")
    
    #Check if the product exists
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        logger.warning(f"Product with ID {product_id} not found")
        raise HTTPException(status_code=404, detail="Product not found")

    #Check if inventory exists
    inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
    if inventory:
        inventory.quantity = inventory_data.quantity
        inventory.last_updated = datetime.now()
        logger.info(f"Inventory for product ID: {product_id} updated successfully")
    else:
        logger.warning(f"Inventory record not found for product ID: {product_id}")
        raise HTTPException(status_code=404, detail="Inventory record not found")

    db.commit()
    db.refresh(inventory)
    logger.info(f"Inventory for product ID: {product_id} committed to the database")
    return inventory