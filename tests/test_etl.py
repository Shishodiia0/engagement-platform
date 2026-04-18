import pytest
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock
from etl.transform import transform_users, transform_events, transform_content
from etl.audit import write_audit_log


# --- Transform Tests ---

def test_transform_users():
    raw = [(1, "  Alice  ", "  ALICE@EXAMPLE.COM  ", datetime(2024, 1, 1))]
    result = transform_users(raw)
    assert result[0]["id"] == 1
    assert result[0]["username"] == "Alice"
    assert result[0]["email"] == "alice@example.com"


def test_transform_users_empty():
    assert transform_users([]) == []


def test_transform_events():
    raw = [(1, 2, 3, "  LOGIN  ", datetime(2024, 1, 1))]
    result = transform_events(raw)
    assert result[0]["id"] == 1
    assert result[0]["user_id"] == 2
    assert result[0]["content_id"] == 3
    assert result[0]["event_type"] == "login"


def test_transform_events_empty():
    assert transform_events([]) == []


def test_transform_content():
    raw = [(1, 2, "  My Title  ", datetime(2024, 1, 1))]
    result = transform_content(raw)
    assert result[0]["id"] == 1
    assert result[0]["user_id"] == 2
    assert result[0]["title"] == "My Title"


def test_transform_content_empty():
    assert transform_content([]) == []


def test_transform_events_none_content_id():
    raw = [(1, 2, None, "view", datetime(2024, 1, 1))]
    result = transform_events(raw)
    assert result[0]["content_id"] is None


# --- Audit Log Tests ---

def test_write_audit_log_success():
    mock_db = MagicMock()
    with patch("etl.audit.SessionLocal", return_value=mock_db):
        write_audit_log(datetime.now(timezone.utc), 100, "success")
        assert mock_db.add.called
        assert mock_db.commit.called
        assert mock_db.close.called


def test_write_audit_log_failure_status():
    mock_db = MagicMock()
    with patch("etl.audit.SessionLocal", return_value=mock_db):
        write_audit_log(datetime.now(timezone.utc), 0, "failed: connection error")
        call_args = mock_db.add.call_args[0][0]
        assert "failed" in call_args.status


# --- Extract Tests ---

def test_get_last_synced_at_no_logs():
    mock_db = MagicMock()
    mock_db.query.return_value.order_by.return_value.first.return_value = None
    with patch("etl.extract.SessionLocal", return_value=mock_db):
        from etl.extract import get_last_synced_at
        result = get_last_synced_at()
        assert result.year == 2000


def test_get_last_synced_at_with_log():
    mock_db = MagicMock()
    expected = datetime(2024, 6, 1, tzinfo=timezone.utc)
    mock_log = MagicMock()
    mock_log.last_synced_at = expected
    mock_db.query.return_value.order_by.return_value.first.return_value = mock_log
    with patch("etl.extract.SessionLocal", return_value=mock_db):
        from etl.extract import get_last_synced_at
        result = get_last_synced_at()
        assert result == expected
