import pytest
from fastapi.testclient import TestClient
from main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.session import get_db
from models.domain.product import Product
from models.domain.inventory import Inventory
from models.domain.order import Order
from models.domain.orderItem import OrderItem
from datetime import datetime
from db.base import Base

#configure test database for reports
SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://postgres:admin@localhost:5432/appytest"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"host": "localhost"})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

#create test client
client = TestClient(app)

#mock db dependency for testing
def override_get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#override the original db dependency in the app
app.dependency_overrides[get_db] = override_get_db

#data for reports
@pytest.fixture
def setup_report_data():
    db = SessionLocal()
    
    #create a product for testing reports
    product = Product(name="Test Product", description="Test product", price=10.0, sku="SKU123")
    db.add(product)
    db.commit()
    db.refresh(product)

    #create inventory for the product
    inventory = Inventory(product_id=product.id, quantity=100)
    db.add(inventory)
    db.commit()
    db.refresh(inventory)

    #create an order with items
    order = Order(status="Completed", total_amount=100.0, created_at=datetime(2025, 1, 1))
    db.add(order)
    db.commit()
    db.refresh(order)

    order_item = OrderItem(order_id=order.id, product_id=product.id, quantity=5, price=10.0)
    db.add(order_item)
    db.commit()
    db.refresh(order_item)

    return product, inventory, order

#test to get products with low stock
def test_get_low_stock(setup_report_data):
    product, _, _ = setup_report_data
    response = client.get(f"/reports/low-stock?threshold=50")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["name"] == product.name

#test to get sales report within date range
def test_get_sales_report(setup_report_data):
    product, _, order = setup_report_data
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2025, 12, 31)
    
    #send GET request to get sales report
    response = client.get(f"/reports/sales?start_date={start_date.isoformat()}&end_date={end_date.isoformat()}")
    
    assert response.status_code == 200
    #check if the sales report contains the correct product id and sales data
    data = response.json()
    assert len(data) > 0
    assert data[0]["product_id"] == product.id
    assert data[0]["total_quantity"] == 5
    assert data[0]["total_sales"] == 50.0
