def test_get_me(auth_client):
    res = auth_client.get("/users/me")
    assert res.status_code == 200
    data = res.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "created_at" in data


def test_get_me_without_token(client):
    res = client.get("/users/me")
    assert res.status_code == 401


def test_get_user_activity(auth_client):
    res = auth_client.get("/users/1/activity")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_get_user_activity_returns_events(auth_client):
    # rate limiter blocks testclient after 30 req/min, use content creation instead
    auth_client.post("/content/create", json={"title": "Post A", "body": "Body"})
    auth_client.post("/content/create", json={"title": "Post B", "body": "Body"})
    res = auth_client.get("/users/1/activity")
    assert res.status_code == 200
    assert len(res.json()) >= 2
