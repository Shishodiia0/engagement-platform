import os
os.environ["TESTING"] = "true"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import backend.database as db_module
from backend.database import Base, get_db
from backend.main import app

SQLITE_URL = "sqlite:///./test.db"

engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine)

# Override the module-level SessionLocal for ETL audit log queries
db_module.engine = engine
db_module.SessionLocal = TestingSessionLocal


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client():
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def auth_client(client):
    client.post("/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    })
    res = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "testpass123"
    })
    token = res.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client
