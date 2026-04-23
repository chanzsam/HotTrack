import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone

from app.config import settings
from app.database import engine, Base, SessionLocal
from app.api.videos import router as videos_router
from app.api.analytics import router as analytics_router
from app.api.tasks import router as tasks_router
from app.api.ai import router as ai_router
from app.scheduler.jobs import run_scheduled_crawl

Base.metadata.create_all(bind=engine)

scheduler = BackgroundScheduler()
US_EASTERN = timezone("America/New_York")


@asynccontextmanager
async def lifespan(app: FastAPI):
    _auto_seed_if_empty()

    scheduler.add_job(
        run_scheduled_crawl,
        CronTrigger(hour=0, minute=0, timezone=US_EASTERN),
        id="scheduled_crawl",
        replace_existing=True,
    )
    scheduler.start()
    yield
    scheduler.shutdown()


def _auto_seed_if_empty():
    from app.models.video import Video
    db = SessionLocal()
    try:
        count = db.query(Video).count()
        if count == 0:
            from app.demo.seed import generate_demo_data
            from app.analyzers.viral import ViralAnalyzer
            from app.analyzers.revenue import RevenueAnalyzer
            n = generate_demo_data(db)
            if n > 0:
                ViralAnalyzer(db).calculate_viral_scores()
                RevenueAnalyzer(db).batch_estimate_revenue()
    except Exception:
        pass
    finally:
        db.close()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS + ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(videos_router, prefix=settings.API_PREFIX)
app.include_router(analytics_router, prefix=settings.API_PREFIX)
app.include_router(tasks_router, prefix=settings.API_PREFIX)
app.include_router(ai_router, prefix=settings.API_PREFIX)

STATIC_DIR = Path(__file__).parent / "static"
if STATIC_DIR.exists():
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")


@app.get("/")
def root():
    if STATIC_DIR.exists() and (STATIC_DIR / "index.html").exists():
        return FileResponse(STATIC_DIR / "index.html")
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": __import__("datetime").datetime.now().isoformat()}


@app.get("/{path:path}")
async def serve_spa(path: str):
    file_path = STATIC_DIR / path
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)
    if STATIC_DIR.exists() and (STATIC_DIR / "index.html").exists():
        return FileResponse(STATIC_DIR / "index.html")
    return {"error": "Not found"}
