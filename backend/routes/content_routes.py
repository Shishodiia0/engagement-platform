from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.database import get_db, Content, Event
from backend.auth.utils import decode_token

router = APIRouter(prefix="/content", tags=["Content"])


class ContentRequest(BaseModel):
    title: str
    body: str


@router.post("/create", status_code=201)
def create_content(req: ContentRequest, user_id: int = Depends(decode_token), db: Session = Depends(get_db)):
    content = Content(user_id=user_id, title=req.title, body=req.body)
    db.add(content)
    db.flush()
    event = Event(user_id=user_id, content_id=content.id, event_type="create")
    db.add(event)
    db.commit()
    db.refresh(content)
    return {"message": "Content created", "content_id": content.id}


@router.get("/all")
def get_all_content(db: Session = Depends(get_db), _: int = Depends(decode_token)):
    contents = db.query(Content).order_by(Content.created_at.desc()).limit(50).all()
    return [{"id": c.id, "user_id": c.user_id, "title": c.title, "created_at": c.created_at} for c in contents]


@router.get("/{content_id}")
def get_content(content_id: int, db: Session = Depends(get_db), _: int = Depends(decode_token)):
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    return {"id": content.id, "user_id": content.user_id, "title": content.title, "body": content.body, "created_at": content.created_at}
