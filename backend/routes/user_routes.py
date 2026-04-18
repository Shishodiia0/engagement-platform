from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db, User, Event
from backend.auth.utils import decode_token

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me")
def get_me(user_id: int = Depends(decode_token), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user.id, "username": user.username, "email": user.email, "created_at": user.created_at}


@router.get("/{user_id}/activity")
def get_user_activity(user_id: int, db: Session = Depends(get_db), _: int = Depends(decode_token)):
    events = db.query(Event).filter(Event.user_id == user_id).order_by(Event.timestamp.desc()).limit(50).all()
    return [{"event_type": e.event_type, "content_id": e.content_id, "timestamp": e.timestamp} for e in events]
