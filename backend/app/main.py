import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api import admin, analysis, auth, intelligence
from app.core.config import get_settings
from app.db.session import Base, SessionLocal, engine
from app.models.entities import APIMetric

settings = get_settings()
app = FastAPI(title=settings.app_name)

allow_all_origins = settings.cors_origins == ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=not allow_all_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def track_api_metrics(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed = (time.perf_counter() - start) * 1000

    if request.url.path not in {"/health"}:
        db = SessionLocal()
        try:
            db.add(APIMetric(endpoint=request.url.path, latency_ms=elapsed, status_code=response.status_code))
            db.commit()
        finally:
            db.close()

    return response


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health():
    return {"status": "ok", "environment": settings.environment, "product": "VisionPilot AI"}


app.include_router(auth.router)
app.include_router(analysis.router)
app.include_router(intelligence.router)
app.include_router(admin.router)
