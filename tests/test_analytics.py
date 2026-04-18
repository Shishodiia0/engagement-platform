from unittest.mock import patch


MOCK_DAU = [{"DATE": "2024-01-01", "ACTIVE_USERS": 5}]
MOCK_EVENTS = [{"EVENT_TYPE": "login", "TOTAL": 10}]
MOCK_CONTENT = [{"CONTENT_ID": 1, "TITLE": "Post 1", "INTERACTIONS": 20}]
MOCK_GROWTH = [{"DATE": "2024-01-01", "NEW_USERS": 3}]


def test_dau_endpoint(auth_client):
    with patch("backend.routes.analytics_routes.run_query", return_value=MOCK_DAU):
        res = auth_client.get("/analytics/dau")
        assert res.status_code == 200
        assert isinstance(res.json(), list)


def test_dau_invalid_days(auth_client):
    res = auth_client.get("/analytics/dau?days=999")
    assert res.status_code == 400


def test_dau_valid_day_options(auth_client):
    for days in [7, 30, 60, 90]:
        with patch("backend.routes.analytics_routes.run_query", return_value=MOCK_DAU):
            res = auth_client.get(f"/analytics/dau?days={days}")
            assert res.status_code == 200


def test_event_breakdown_endpoint(auth_client):
    with patch("backend.routes.analytics_routes.run_query", return_value=MOCK_EVENTS):
        res = auth_client.get("/analytics/event-breakdown")
        assert res.status_code == 200
        assert isinstance(res.json(), list)


def test_event_breakdown_invalid_days(auth_client):
    res = auth_client.get("/analytics/event-breakdown?days=15")
    assert res.status_code == 400


def test_top_content_endpoint(auth_client):
    with patch("backend.routes.analytics_routes.run_query", return_value=MOCK_CONTENT):
        res = auth_client.get("/analytics/top-content")
        assert res.status_code == 200
        assert isinstance(res.json(), list)


def test_user_growth_endpoint(auth_client):
    with patch("backend.routes.analytics_routes.run_query", return_value=MOCK_GROWTH):
        res = auth_client.get("/analytics/user-growth")
        assert res.status_code == 200
        assert isinstance(res.json(), list)


def test_etl_status_no_runs(auth_client):
    # ETLAuditLog gets a default row from SQLite on startup, check it returns valid response
    res = auth_client.get("/analytics/etl-status")
    assert res.status_code == 200
    data = res.json()
    assert "status" in data


def test_etl_status_with_run(auth_client):
    from datetime import datetime, timezone
    from tests.conftest import TestingSessionLocal
    from backend.database import ETLAuditLog
    db = TestingSessionLocal()
    db.add(ETLAuditLog(
        last_synced_at=datetime.now(timezone.utc),
        rows_extracted=100,
        status="success",
        ran_at=datetime.now(timezone.utc)
    ))
    db.commit()
    db.close()
    res = auth_client.get("/analytics/etl-status")
    assert res.status_code == 200
    assert res.json()["status"] == "success"


def test_analytics_without_token(client):
    for endpoint in ["/analytics/dau", "/analytics/event-breakdown", "/analytics/top-content", "/analytics/user-growth"]:
        res = client.get(endpoint)
        assert res.status_code == 401
