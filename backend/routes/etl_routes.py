from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timezone
from backend.auth.utils import decode_token
from etl.extract import get_last_synced_at, extract_data
from etl.transform import transform_users, transform_events, transform_content
from etl.load import load_users, load_content, load_events
from etl.audit import write_audit_log

router = APIRouter(prefix="/etl", tags=["ETL"])


@router.post("/trigger")
def trigger_etl(_: int = Depends(decode_token)):
    try:
        last_synced_at = get_last_synced_at()
        users, events, content = extract_data(last_synced_at)
        load_users(transform_users(users))
        load_content(transform_content(content))
        load_events(transform_events(events))
        total_rows = len(users) + len(events) + len(content)
        write_audit_log(datetime.now(timezone.utc), total_rows, "success")
        return {"message": "ETL completed", "rows_synced": total_rows}
    except Exception as e:
        write_audit_log(datetime.now(timezone.utc), 0, f"failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
