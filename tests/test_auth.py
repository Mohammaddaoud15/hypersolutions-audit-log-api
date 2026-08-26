def test_register_success(client):
    payload = {
        "username": "testuser",
        "password": "securepassword123",
        "role": "User"
    }
    
    response = client.post("/auth/register", json=payload)
    
    assert response.status_code == 201
    
    data = response.json()
    assert data["username"] == "testuser"
    assert "id" in data
    assert "password" not in data 

def test_register_duplicate_user(client):
    payload = {
        "username": "duplicate_user",
        "password": "password123",
        "role": "User"
    }
    response_1 = client.post("/auth/register", json=payload)
    assert response_1.status_code == 201
    
    response_2 = client.post("/auth/register", json=payload)
    assert response_2.status_code >= 400

def test_register_default_role(client):
    payload = {
        "username": "newuser",
        "password": "password123",
    }

    response = client.post("/auth/register", json=payload)

    assert response.status_code == 201
    assert response.json()["role"] == "User"

def test_login_success(client):
    client.post("/auth/register", json={
        "username": "logintest",
        "password": "loginpassword123",
        "role": "Admin"
    })

    login_data = {
        "username": "logintest", 
        "password": "loginpassword123"
    }
    
    response = client.post("/auth/login", data=login_data)
    
    assert response.status_code == 200
    
    data = response.json()
    assert "access_token" in data
    assert data["token_type"].lower() == "bearer"

def test_login_invalid_password(client):
    client.post("/auth/register", json={
        "username": "secureuser",
        "password": "correctpassword",
        "role": "User"
    })

    response = client.post("/auth/login", data={
        "username": "secureuser",
        "password": "wrongpassword"
    })
    
    assert response.status_code == 401
    assert "detail" in response.json()