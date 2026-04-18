import pytest

VALID_EVENTS = ["login", "view", "like", "comment", "create"]


@pytest.mark.parametrize("event_type", VALID_EVENTS)
def test_track_valid_events(auth_client, event_type):
    res = auth_client.post("/events/track", json={"event_type": event_type})
    assert res.status_code == 201
    assert res.json()["message"] == "Event tracked"


def test_track_event_with_content_id(auth_client):
    create_res = auth_client.post("/content/create", json={"title": "Post", "body": "Body"})
    content_id = create_res.json()["content_id"]
    res = auth_client.post("/events/track", json={"event_type": "view", "content_id": content_id})
    assert res.status_code == 201


def test_track_invalid_event_type(auth_client):
    res = auth_client.post("/events/track", json={"event_type": "invalid_event"})
    assert res.status_code == 400


def test_track_event_without_token(client):
    res = client.post("/events/track", json={"event_type": "login"})
    assert res.status_code == 401


def test_get_recent_events(auth_client):
    auth_client.post("/events/track", json={"event_type": "login"})
    auth_client.post("/events/track", json={"event_type": "view"})
    res = auth_client.get("/events/recent")
    assert res.status_code == 200
    assert isinstance(res.json(), list)
    assert len(res.json()) >= 2


def test_recent_events_limit(auth_client):
    for _ in range(25):
        auth_client.post("/events/track", json={"event_type": "login"})
    res = auth_client.get("/events/recent")
    assert res.status_code == 200
    assert len(res.json()) <= 20


def test_recent_events_without_token(client):
    res = client.get("/events/recent")
    assert res.status_code == 401
