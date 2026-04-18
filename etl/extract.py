from sqlalchemy import text
from backend.database import SessionLocal, ETLAuditLog
from datetime import datetime, timezone


def get_last_synced_at():
    db = SessionLocal()
    log = db.query(ETLAuditLog).order_by(ETLAuditLog.ran_at.desc()).first()
    db.close()
    return log.last_synced_at if log else datetime(2000, 1, 1, tzinfo=timezone.utc)


def extract_data(last_synced_at: datetime):
    db = SessionLocal()
    users = db.execute(text(
        "SELECT id, username, email, created_at FROM users WHERE created_at > :ts"
    ), {"ts": last_synced_at}).fetchall()

    events = db.execute(text(
        "SELECT id, user_id, content_id, event_type, timestamp FROM events WHERE timestamp > :ts"
    ), {"ts": last_synced_at}).fetchall()

    content = db.execute(text(
        "SELECT id, user_id, title, created_at FROM content WHERE created_at > :ts"
    ), {"ts": last_synced_at}).fetchall()

    db.close()
    return users, events, content
