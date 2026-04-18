from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, timezone
import os

Base = declarative_base()


def get_engine():
    from backend.config import DATABASE_URL
    return create_engine(DATABASE_URL)


def get_session_local():
    return sessionmaker(bind=get_engine())


# Only create real engine if not testing
if os.getenv("TESTING") != "true":
    from backend.config import DATABASE_URL
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
else:
    engine = None
    SessionLocal = None


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Content(Base):
    __tablename__ = "content"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    body = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content_id = Column(Integer, ForeignKey("content.id"), nullable=True)
    event_type = Column(String, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class ETLAuditLog(Base):
    __tablename__ = "etl_audit_log"
    id = Column(Integer, primary_key=True, index=True)
    last_synced_at = Column(DateTime, nullable=False)
    rows_extracted = Column(Integer, default=0)
    status = Column(String, default="success")
    ran_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
