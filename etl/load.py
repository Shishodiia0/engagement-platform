import snowflake.connector
from backend.config import SF_ACCOUNT, SF_USER, SF_PASSWORD, SF_WAREHOUSE, SF_DATABASE, SF_SCHEMA


def _get_connection():
    return snowflake.connector.connect(
        account=SF_ACCOUNT, user=SF_USER, password=SF_PASSWORD,
        warehouse=SF_WAREHOUSE, database=SF_DATABASE, schema=SF_SCHEMA
    )


def _merge(table: str, source_cols: list, key: str, rows: list, values_fn):
    if not rows:
        return
    conn = _get_connection()
    cur = conn.cursor()
    cols = ", ".join(source_cols)
    placeholders = ", ".join(["%s"] * len(source_cols))
    aliases = ", ".join(f"%s AS {c}" for c in source_cols)
    sql = (
        f"MERGE INTO {table} AS target "
        f"USING (SELECT {aliases}) AS source ON target.{key} = source.{key} "
        f"WHEN NOT MATCHED THEN INSERT ({cols}) VALUES ({placeholders})"
    )
    for row in rows:
        vals = values_fn(row)
        cur.execute(sql, vals + vals)
    cur.close()
    conn.close()


def load_users(users):
    _merge("DIM_USERS", ["ID", "USERNAME", "EMAIL", "CREATED_AT"], "ID", users,
           lambda u: (u["id"], u["username"], u["email"], u["created_at"]))


def load_content(content):
    _merge("DIM_CONTENT", ["ID", "USER_ID", "TITLE", "CREATED_AT"], "ID", content,
           lambda c: (c["id"], c["user_id"], c["title"], c["created_at"]))


def load_events(events):
    _merge("FACT_EVENTS", ["ID", "USER_ID", "CONTENT_ID", "EVENT_TYPE", "TIMESTAMP"], "ID", events,
           lambda e: (e["id"], e["user_id"], e["content_id"], e["event_type"], e["timestamp"]))
