import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from db.base import Base
from db.session import get_db
from models.domain.product import Product
from schemas.product import ProductCreate
from unittest import mock
from utils.dependencies import get_current_user

# Configuración de la base de datos de prueba
SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://postgres:admin@localhost:5432/appytest"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"host": "localhost"})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

# Usamos la base de datos de pruebas en lugar de la regular
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def mock_get_current_user():
    # Mockear la función get_current_user
    with mock.patch("utils.dependencies.get_current_user") as mock_get_user:
        # Simulamos que el usuario está autenticado (puedes devolver lo que necesites)
        mock_get_user.return_value = {"sub": "test_user", "role": "admin"}
        yield mock_get_user  # El mock se utilizará durante el test

client = TestClient(app)

# Datos de ejemplo para las pruebas
product_data = {
    "name": "Test Product",
    "description": "This is a test product.",
    "price": 99.99,
    "sku": "TEST1234"
}

@pytest.fixture(scope="function")
def setup_database():
    # Limpiar la base de datos antes de cada prueba
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# Pruebas de los endpoints
def test_create_product(setup_database):
    response = client.post("/products/", json=product_data)

    print(response.json())  # Imprime la respuesta para depurar

    assert response.status_code == 201
    assert response.json()["name"] == product_data["name"]

def test_get_products(setup_database):
    # Crear producto
    client.post("/products/", json=product_data)
    response = client.get("/products/")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == product_data["name"]

def test_get_product_by_id(setup_database):
    # Obtener producto por ID
    post_response = client.post("/products/", json=product_data)
    product_id = post_response.json()["id"]

    response = client.get(f"/products/{product_id}")
    assert response.status_code == 200
    assert response.json()["name"] == product_data["name"]

def test_update_product(setup_database):
    # Actualizar producto
    post_response = client.post("/products/", json=product_data)
    product_id = post_response.json()["id"]

    updated_data = {
        "name": "Updated Product",
        "description": "Updated description.",
        "price": 120.00,
        "sku": "UPDATED1234"
    }

    response = client.put(f"/products/{product_id}", json=updated_data)
    assert response.status_code == 200
    assert response.json()["name"] == updated_data["name"]

def test_delete_product(setup_database):
    # Eliminar producto
    post_response = client.post("/products/", json=product_data)
    product_id = post_response.json()["id"]

    delete_response = client.delete(f"/products/{product_id}")
    assert delete_response.status_code == 204

    # Verificar que el producto ha sido eliminado
    get_response = client.get(f"/products/{product_id}")
    assert get_response.status_code == 404
