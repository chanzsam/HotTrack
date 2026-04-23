import os
import logging
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

logger = logging.getLogger(__name__)

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
            seeded = False
            
            if settings.YOUTUBE_API_ENABLED:
                try:
                    from app.crawlers.youtube import YouTubeCrawler
                    from app.analyzers.viral import ViralAnalyzer
                    from app.analyzers.revenue import RevenueAnalyzer
                    
                    crawler = YouTubeCrawler()
                    videos = crawler.get_trending_videos(region_code="US", max_results=50)
                    if videos:
                        crawler.save_videos_to_db(videos, db)
                        ViralAnalyzer(db).calculate_viral_scores()
                        RevenueAnalyzer(db).batch_estimate_revenue()
                        seeded = True
                        logger.info(f"使用 YouTube API 获取了 {len(videos)} 条真实数据")
                except Exception as e:
                    logger.warning(f"YouTube API 获取失败: {e}")
            
            if settings.TIKHUB_ENABLED and not seeded:
                try:
                    from app.crawlers.tiktok import TikTokCrawler
                    from app.analyzers.viral import ViralAnalyzer
                    from app.analyzers.revenue import RevenueAnalyzer
                    
                    crawler = TikTokCrawler(tikhub_api_key=settings.TIKHUB_API_KEY)
                    videos = crawler.get_trending_videos(count=50)
                    if videos:
                        crawler.save_videos_to_db(videos, db)
                        ViralAnalyzer(db).calculate_viral_scores()
                        RevenueAnalyzer(db).batch_estimate_revenue()
                        seeded = True
                        logger.info(f"使用 TikHub API 获取了 {len(videos)} 条真实数据")
                except Exception as e:
                    logger.warning(f"TikHub API 获取失败: {e}")
            
            if not seeded:
                from app.demo.seed import generate_demo_data
                from app.analyzers.viral import ViralAnalyzer
                from app.analyzers.revenue import RevenueAnalyzer
                n = generate_demo_data(db)
                if n > 0:
                    ViralAnalyzer(db).calculate_viral_scores()
                    RevenueAnalyzer(db).batch_estimate_revenue()
                    logger.info(f"使用演示数据: {n} 条")
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
