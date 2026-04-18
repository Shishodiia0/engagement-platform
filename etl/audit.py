from backend.database import SessionLocal, ETLAuditLog
from datetime import datetime, timezone


def write_audit_log(last_synced_at: datetime, rows_extracted: int, status: str):
    db = SessionLocal()
    db.add(ETLAuditLog(
        last_synced_at=last_synced_at,
        rows_extracted=rows_extracted,
        status=status,
        ran_at=datetime.now(timezone.utc)
    ))
    db.commit()
    db.close()
