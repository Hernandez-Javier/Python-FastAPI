import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from models.domain.product import Product
from schemas.product import ProductCreate, ProductResponse
from db.session import get_db
from typing import List
from models.domain.inventory import Inventory
from slowapi import Limiter
from slowapi.util import get_remote_address

# Configure the logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

router = APIRouter()

limiter = Limiter(key_func=get_remote_address)

#create a new product
@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def create_product(request: Request, product: ProductCreate, db: Session = Depends(get_db)):  # Added 'request' argument
    # Log the incoming product creation request
    logger.info(f"Received request to create product with name: {product.name}, SKU: {product.sku}")

    try:
        # Create the product record in the Product table
        db_product = Product(
            name=product.name,
            description=product.description,
            price=product.price,
            sku=product.sku
        )
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        logger.info(f"Product created successfully with ID: {db_product.id}")

        # Create an inventory record for the new product with quantity 1
        db_inventory = Inventory(
            product_id=db_product.id,  # Link inventory to the new product
            quantity=1  # Set the initial quantity to 1
        )
        db.add(db_inventory)
        db.commit()
        db.refresh(db_inventory)
        logger.info(f"Inventory record created for product ID {db_product.id} with quantity: {db_inventory.quantity}")

        # Return the created product
        return db_product

    except Exception as e:
        # Log the error and raise an HTTPException
        logger.error(f"Error creating product: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

#get all products
@router.get("/", response_model=List[ProductResponse])
@limiter.limit("5/minute")
def get_products(request: Request, db: Session = Depends(get_db)):  # Added 'request' argument
    logger.info("Fetching all products")
    products = db.query(Product).all()
    logger.info(f"Found {len(products)} products")
    return products

#get a product by id
@router.get("/{product_id}", response_model=ProductResponse)
@limiter.limit("3/minute")
def get_product(request: Request, product_id: int, db: Session = Depends(get_db)):  # Added 'request' argument
    logger.info(f"Fetching product with ID: {product_id}")
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        logger.warning(f"Product with ID {product_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    logger.info(f"Found product with ID {product_id}")
    return product

#modify a product
@router.put("/{product_id}", response_model=ProductResponse)
@limiter.limit("3/minute")
def update_product(request: Request, product_id: int, product: ProductCreate, db: Session = Depends(get_db)):  # Added 'request' argument
    logger.info(f"Updating product with ID: {product_id}")
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        logger.warning(f"Product with ID {product_id} not found for update")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    db_product.name = product.name
    db_product.description = product.description
    db_product.price = product.price
    db_product.sku = product.sku
    db.commit()
    db.refresh(db_product)
    logger.info(f"Product with ID {product_id} updated successfully")
    return db_product

#delete a product
@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("2/minute")
def delete_product(request: Request, product_id: int, db: Session = Depends(get_db)):  # Added 'request' argument
    logger.info(f"Attempting to delete product with ID: {product_id}")
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        logger.warning(f"Product with ID {product_id} not found for deletion")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    db.delete(db_product)
    db.commit()
    logger.info(f"Product with ID {product_id} deleted successfully")