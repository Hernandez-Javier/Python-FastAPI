import pytest
from fastapi.testclient import TestClient
from main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.session import get_db
from models.domain.product import Product
from models.domain.order import Order
from models.domain.orderItem import OrderItem
from models.domain.inventory import Inventory
from db.base import Base

#configure test db
SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://postgres:admin@localhost:5432/appytest"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"host": "localhost"})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#create testing db
Base.metadata.create_all(bind=engine)

client = TestClient(app)

#test dependecy
def override_get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#uses testing db
app.dependency_overrides[get_db] = override_get_db

#testing data
@pytest.fixture
def setup_data():
    db = SessionLocal()
    product = Product(name="Test Product", description="Test product", price=10.0, sku="SKU123")
    db.add(product)
    db.commit()
    db.refresh(product)

    inventory = Inventory(product_id=product.id, quantity=100)
    db.add(inventory)
    db.commit()
    db.refresh(inventory)
    
    order = Order(status="Pending", total_amount=50.0)
    db.add(order)
    db.commit()
    db.refresh(order)
    
    order_item = OrderItem(order_id=order.id, product_id=product.id, quantity=5, price=10.0)
    db.add(order_item)
    db.commit()
    
    return order, product

#create a new order
def test_create_order(setup_data):
    order, product = setup_data
    order_data = {
        "status": "Pending",
        "total_amount": 50.0,
        "items": [{"product_id": product.id, "quantity": 5, "price": 10.0}]
    }
    
    response = client.post("/orders/", json=order_data)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "Pending"
    assert data["total_amount"] == 50.0

#get all orders
def test_get_orders():
    response = client.get("/orders/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

#get order by id
def test_get_order_by_id(setup_data):
    order, _ = setup_data
    response = client.get(f"/orders/{order.id}")
    assert response.status_code == 200
    assert response.json()["id"] == order.id

#modify order status
def test_update_order_status(setup_data):
    order, _ = setup_data
    new_status = "Shipped"
    response = client.put(f"/orders/{order.id}/status", json={"status": new_status})
    assert response.status_code == 200
    assert response.json()["status"] == new_status
