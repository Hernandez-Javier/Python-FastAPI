import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from db.base import Base
from db.session import get_db
from models.domain.inventory import Inventory
from models.domain.product import Product
from schemas.inventory import InventoryUpdate, InventoryResponse
from unittest import mock
from datetime import datetime

#db data
SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://postgres:admin@localhost:5432/appytest"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"host": "localhost"})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

#replace the original db for the testing one
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

#data for testing
product_data = {
    "name": "Test Product",
    "description": "This is a test product.",
    "price": 99.99,
    "sku": "TEST1234"
}

inventory_data = {
    "product_id": 1,
    "quantity": 100
}

updated_inventory_data = InventoryUpdate(quantity=150)

@pytest.fixture(scope="function")
def setup_database():
    #cleandb before testing
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    product = Product(**product_data)
    db = TestingSessionLocal()
    db.add(product)
    db.commit()
    db.refresh(product)
    
    #inventory item for testing
    inventory = Inventory(product_id=product.id, quantity=inventory_data["quantity"])
    db.add(inventory)
    db.commit()
    db.refresh(inventory)

    yield db

    #clean after testing
    Base.metadata.drop_all(bind=engine)

#get all inventory record test
def test_get_inventory(setup_database):
    response = client.get("/inventory/")
    assert response.status_code == 200
    assert len(response.json()) > 0

#get inventory by id
def test_get_inventory_by_product(setup_database):
    product_id = 1
    response = client.get(f"/inventory/{product_id}")
    assert response.status_code == 200
    assert response.json()["product_id"] == product_id
    assert response.json()["quantity"] == inventory_data["quantity"]

#test a non existing iventory item
def test_get_inventory_by_nonexistent_product(setup_database):
    response = client.get("/inventory/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Inventory record not found"

#modify an inventory entry
def test_update_inventory(setup_database):
    product_id = 1
    response = client.put(f"/inventory/{product_id}", json=updated_inventory_data.model_dump())
    assert response.status_code == 200
    assert response.json()["quantity"] == updated_inventory_data.quantity