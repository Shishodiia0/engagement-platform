from fastapi import FastAPI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from backend.database import init_db
from backend.routes.auth_routes import router as auth_router
from backend.routes.user_routes import router as user_router
from backend.routes.content_routes import router as content_router
from backend.routes.event_routes import router as event_router
from backend.routes.analytics_routes import router as analytics_router
from backend.routes.etl_routes import router as etl_router

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="User Engagement Analytics Platform", version="1.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(content_router)
app.include_router(event_router)
app.include_router(analytics_router)
app.include_router(etl_router)


@app.on_event("startup")
def startup():
    import os
    if os.getenv("TESTING") != "true":
        init_db()


@app.get("/")
def root():
    return {"message": "Engagement Platform API is running", "version": "1.0.0", "status": "healthy"}
