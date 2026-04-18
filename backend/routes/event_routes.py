from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request
from backend.database import get_db, Event
from backend.auth.utils import decode_token

router = APIRouter(prefix="/events", tags=["Events"])
limiter = Limiter(key_func=get_remote_address)

VALID_EVENTS = {"login", "view", "like", "comment", "create"}


class EventRequest(BaseModel):
    event_type: str
    content_id: Optional[int] = None


@router.post("/track", status_code=201)
@limiter.limit("30/minute")
def track_event(request: Request, req: EventRequest, user_id: int = Depends(decode_token), db: Session = Depends(get_db)):
    if req.event_type not in VALID_EVENTS:
        raise HTTPException(status_code=400, detail=f"Invalid event type. Valid: {VALID_EVENTS}")
    db.add(Event(user_id=user_id, content_id=req.content_id, event_type=req.event_type))
    db.commit()
    return {"message": "Event tracked"}


@router.get("/recent")
def recent_events(db: Session = Depends(get_db), _: int = Depends(decode_token)):
    events = db.query(Event).order_by(Event.timestamp.desc()).limit(20).all()
    return [{"user_id": e.user_id, "event_type": e.event_type, "content_id": e.content_id, "timestamp": e.timestamp} for e in events]
