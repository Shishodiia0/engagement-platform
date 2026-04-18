def test_create_content(auth_client):
    res = auth_client.post("/content/create", json={
        "title": "Test Post",
        "body": "This is a test body."
    })
    assert res.status_code == 201
    assert res.json()["message"] == "Content created"
    assert "content_id" in res.json()


def test_create_content_without_token(client):
    res = client.post("/content/create", json={
        "title": "Test Post",
        "body": "Body"
    })
    assert res.status_code == 401


def test_get_all_content(auth_client):
    auth_client.post("/content/create", json={"title": "Post 1", "body": "Body 1"})
    auth_client.post("/content/create", json={"title": "Post 2", "body": "Body 2"})
    res = auth_client.get("/content/all")
    assert res.status_code == 200
    assert len(res.json()) >= 2


def test_get_content_by_id(auth_client):
    create_res = auth_client.post("/content/create", json={
        "title": "Single Post",
        "body": "Single body"
    })
    content_id = create_res.json()["content_id"]
    res = auth_client.get(f"/content/{content_id}")
    assert res.status_code == 200
    assert res.json()["title"] == "Single Post"
    assert res.json()["body"] == "Single body"


def test_get_nonexistent_content(auth_client):
    res = auth_client.get("/content/99999")
    assert res.status_code == 404


def test_create_content_also_tracks_event(auth_client):
    auth_client.post("/content/create", json={"title": "Event Post", "body": "Body"})
    res = auth_client.get("/events/recent")
    event_types = [e["event_type"] for e in res.json()]
    assert "create" in event_types
