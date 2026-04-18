def transform_users(users):
    return [
        {
            "id": row[0],
            "username": str(row[1]).strip(),
            "email": str(row[2]).strip().lower(),
            "created_at": row[3]
        }
        for row in users
    ]


def transform_events(events):
    return [
        {
            "id": row[0],
            "user_id": row[1],
            "content_id": row[2],
            "event_type": str(row[3]).strip().lower(),
            "timestamp": row[4]
        }
        for row in events
    ]


def transform_content(content):
    return [
        {
            "id": row[0],
            "user_id": row[1],
            "title": str(row[2]).strip(),
            "created_at": row[3]
        }
        for row in content
    ]
