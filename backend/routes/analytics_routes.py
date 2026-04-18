from fastapi import APIRouter, Depends, HTTPException
from backend.auth.utils import decode_token
from backend.database import SessionLocal, ETLAuditLog
from backend.config import SF_ACCOUNT, SF_USER, SF_PASSWORD, SF_WAREHOUSE, SF_DATABASE, SF_SCHEMA
import snowflake.connector

router = APIRouter(prefix="/analytics", tags=["Analytics"])


def get_sf_connection():
    return snowflake.connector.connect(
        account=SF_ACCOUNT, user=SF_USER, password=SF_PASSWORD,
        warehouse=SF_WAREHOUSE, database=SF_DATABASE, schema=SF_SCHEMA
    )


def run_query(query: str, params: tuple = ()):
    try:
        conn = get_sf_connection()
        cur = conn.cursor()
        cur.execute(query, params)
        columns = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def validate_days(days: int) -> int:
    if days not in (7, 30, 60, 90):
        raise HTTPException(status_code=400, detail="days must be 7, 30, 60, or 90")
    return days


@router.get("/dau")
def daily_active_users(days: int = 30, _: int = Depends(decode_token)):
    days = validate_days(days)
    return run_query(
        "SELECT DATE(TIMESTAMP) AS date, COUNT(DISTINCT USER_ID) AS active_users "
        "FROM FACT_EVENTS WHERE TIMESTAMP >= DATEADD(day, %s, CURRENT_DATE) "
        "GROUP BY DATE(TIMESTAMP) ORDER BY date ASC",
        (-days,)
    )


@router.get("/event-breakdown")
def event_breakdown(days: int = 30, _: int = Depends(decode_token)):
    days = validate_days(days)
    return run_query(
        "SELECT EVENT_TYPE, COUNT(*) AS total FROM FACT_EVENTS "
        "WHERE TIMESTAMP >= DATEADD(day, %s, CURRENT_DATE) "
        "GROUP BY EVENT_TYPE ORDER BY total DESC",
        (-days,)
    )


@router.get("/top-content")
def top_content(days: int = 30, _: int = Depends(decode_token)):
    days = validate_days(days)
    return run_query(
        "SELECT f.CONTENT_ID, c.TITLE, COUNT(*) AS interactions "
        "FROM FACT_EVENTS f JOIN DIM_CONTENT c ON f.CONTENT_ID = c.ID "
        "WHERE f.CONTENT_ID IS NOT NULL AND f.TIMESTAMP >= DATEADD(day, %s, CURRENT_DATE) "
        "GROUP BY f.CONTENT_ID, c.TITLE ORDER BY interactions DESC LIMIT 10",
        (-days,)
    )


@router.get("/user-growth")
def user_growth(days: int = 30, _: int = Depends(decode_token)):
    days = validate_days(days)
    return run_query(
        "SELECT DATE(CREATED_AT) AS date, COUNT(*) AS new_users FROM DIM_USERS "
        "WHERE CREATED_AT >= DATEADD(day, %s, CURRENT_DATE) "
        "GROUP BY DATE(CREATED_AT) ORDER BY date ASC",
        (-days,)
    )


@router.get("/etl-status")
def etl_status(_: int = Depends(decode_token)):
    import backend.database as db_module
    db = db_module.SessionLocal()
    log = db.query(ETLAuditLog).order_by(ETLAuditLog.ran_at.desc()).first()
    db.close()
    if not log:
        return {"status": "No ETL runs yet"}
    return {"last_synced_at": log.last_synced_at, "rows_extracted": log.rows_extracted, "status": log.status, "ran_at": log.ran_at}
