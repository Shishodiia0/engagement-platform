def test_register_success(client):
    res = client.post("/auth/register", json={
        "username": "newuser",
        "email": "new@example.com",
        "password": "pass123"
    })
    assert res.status_code == 201
    assert res.json()["message"] == "User registered successfully"
    assert "user_id" in res.json()


def test_register_duplicate_email(client):
    payload = {"username": "user1", "email": "dup@example.com", "password": "pass123"}
    client.post("/auth/register", json=payload)
    res = client.post("/auth/register", json={**payload, "username": "user2"})
    assert res.status_code == 400
    assert "already registered" in res.json()["detail"]


def test_register_invalid_email(client):
    res = client.post("/auth/register", json={
        "username": "user1",
        "email": "not-an-email",
        "password": "pass123"
    })
    assert res.status_code == 422


def test_login_success(client):
    client.post("/auth/register", json={
        "username": "loginuser",
        "email": "login@example.com",
        "password": "pass123"
    })
    res = client.post("/auth/login", json={
        "email": "login@example.com",
        "password": "pass123"
    })
    assert res.status_code == 200
    assert "access_token" in res.json()
    assert res.json()["token_type"] == "bearer"


def test_login_wrong_password(client):
    client.post("/auth/register", json={
        "username": "loginuser",
        "email": "login@example.com",
        "password": "pass123"
    })
    res = client.post("/auth/login", json={
        "email": "login@example.com",
        "password": "wrongpass"
    })
    assert res.status_code == 401


def test_login_nonexistent_user(client):
    res = client.post("/auth/login", json={
        "email": "ghost@example.com",
        "password": "pass123"
    })
    assert res.status_code == 401


def test_protected_route_without_token(client):
    res = client.get("/users/me")
    assert res.status_code == 401
