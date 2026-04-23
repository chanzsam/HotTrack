import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.config import settings
from app.crawlers.youtube import YouTubeCrawler
from app.crawlers.tiktok import TikTokCrawler
from app.analyzers.viral import ViralAnalyzer
from app.analyzers.revenue import RevenueAnalyzer

logger = logging.getLogger(__name__)


def run_scheduled_crawl():
    db = SessionLocal()
    try:
        logger.info(f"[定时任务] 开始数据采集 - {datetime.now(timezone.utc).isoformat()}")

        yt_crawler = YouTubeCrawler()
        yt_videos = yt_crawler.get_trending_videos(region_code="US")
        if yt_videos:
            yt_crawler.save_videos_to_db(yt_videos, db)
            logger.info(f"[定时任务] YouTube 采集 {len(yt_videos)} 条")

        tikhub_key = settings.TIKHUB_API_KEY if settings.TIKHUB_ENABLED else None
        tt_crawler = TikTokCrawler(tikhub_api_key=tikhub_key)
        tt_videos = tt_crawler.get_trending_videos()
        if tt_videos:
            tt_crawler.save_videos_to_db(tt_videos, db)
            logger.info(f"[定时任务] TikTok 采集 {len(tt_videos)} 条")

        viral_analyzer = ViralAnalyzer(db)
        viral_analyzer.calculate_viral_scores()
        logger.info("[定时任务] 爆红指数计算完成")

        revenue_analyzer = RevenueAnalyzer(db)
        count = revenue_analyzer.batch_estimate_revenue()
        logger.info(f"[定时任务] 收入估算完成，处理 {count} 条")

    except Exception as e:
        logger.error(f"[定时任务] 执行出错: {e}")
    finally:
        db.close()
