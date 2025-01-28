from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# Testing
def test_login():
    #login simulation
    login_data = {"username": "admin", "password": "123456"}
    response = client.post("/login", json=login_data)
    
    #check login succes
    assert response.status_code == 200
    assert "access_token" in response.json()

    #get token
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    #acces to protected endpoint
    protected_response = client.get("/products", headers=headers)
    assert protected_response.status_code == 200
