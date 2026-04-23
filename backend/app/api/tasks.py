from fastapi import APIRouter, Depends, Query, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.crawlers.youtube import YouTubeCrawler
from app.crawlers.tiktok import TikTokCrawler
from app.analyzers.viral import ViralAnalyzer
from app.analyzers.revenue import RevenueAnalyzer
from app.config import settings

router = APIRouter(prefix="/crawl", tags=["crawl"])


@router.get("/config-status")
def get_config_status():
    return {
        "youtube_api_key_configured": bool(settings.YOUTUBE_API_KEY),
        "youtube_api_key_length": len(settings.YOUTUBE_API_KEY) if settings.YOUTUBE_API_KEY else 0,
        "youtube_api_enabled": settings.YOUTUBE_API_ENABLED,
        "tikhub_api_key_configured": bool(settings.TIKHUB_API_KEY),
        "tikhub_api_key_length": len(settings.TIKHUB_API_KEY) if settings.TIKHUB_API_KEY else 0,
        "tikhub_enabled": settings.TIKHUB_ENABLED,
    }


@router.get("/test-youtube-api")
def test_youtube_api():
    if not settings.YOUTUBE_API_KEY:
        return {"success": False, "error": "YouTube API Key 未配置"}
    
    try:
        crawler = YouTubeCrawler()
        videos = crawler.get_trending_videos(region_code="US", max_results=5)
        if videos:
            return {
                "success": True, 
                "count": len(videos),
                "sample": {
                    "title": videos[0].get("title", "")[:50],
                    "views": videos[0].get("view_count", 0),
                }
            }
        return {"success": False, "error": "未获取到数据，请检查 API Key 是否有效"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/calculate-revenue")
def calculate_revenue(db: Session = Depends(get_db)):
    try:
        revenue_analyzer = RevenueAnalyzer(db)
        count = revenue_analyzer.batch_estimate_revenue()
        return {"success": True, "message": f"成功估算 {count} 条视频收入", "count": count}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/schedule")
def get_schedule_status():
    from app.main import scheduler, US_EASTERN
    jobs = scheduler.get_jobs()
    result = []
    for job in jobs:
        next_run = job.next_run_time
        result.append({
            "id": job.id,
            "name": job.name or job.func.__name__,
            "next_run": next_run.isoformat() if next_run else None,
            "next_run_eastern": next_run.astimezone(US_EASTERN).strftime("%Y-%m-%d %H:%M:%S %Z") if next_run else None,
            "trigger": str(job.trigger),
        })
    return {
        "timezone": "America/New_York (北美东部时间)",
        "schedule": "每天 00:00 执行",
        "jobs": result,
    }


@router.post("/trigger")
def trigger_crawl_now(db: Session = Depends(get_db)):
    from app.scheduler.jobs import run_scheduled_crawl
    run_scheduled_crawl()
    return {"message": "数据更新已触发", "timestamp": datetime.now().isoformat()}


def _run_post_crawl_analysis(db: Session):
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        viral_analyzer = ViralAnalyzer(db)
        count = viral_analyzer.calculate_viral_scores()
        logger.info(f"[分析] 爆红指数计算完成: {count} 条")
    except Exception as e:
        logger.error(f"[分析] 爆红指数计算失败: {e}")
    
    try:
        revenue_analyzer = RevenueAnalyzer(db)
        count = revenue_analyzer.batch_estimate_revenue()
        logger.info(f"[分析] 收入估算完成: {count} 条")
    except Exception as e:
        logger.error(f"[分析] 收入估算失败: {e}")


@router.post("/youtube")
def crawl_youtube(
    type: str = Query("popular", description="采集类型: popular, trending, category"),
    region: str = Query("US", description="区域代码"),
    max_results: int = Query(50, ge=1, le=50),
    db: Session = Depends(get_db),
):
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"[YouTube 采集] 开始采集, type={type}, region={region}, max_results={max_results}")
    logger.info(f"[YouTube 采集] YOUTUBE_API_ENABLED={settings.YOUTUBE_API_ENABLED}")
    logger.info(f"[YouTube 采集] YOUTUBE_API_KEY 长度={len(settings.YOUTUBE_API_KEY) if settings.YOUTUBE_API_KEY else 0}")
    
    try:
        crawler = YouTubeCrawler()
        videos = []

        if type == "trending":
            videos = crawler.get_trending_videos(region_code=region, max_results=max_results)
        elif type == "category":
            videos = crawler.get_trending_videos(region_code=region, category_id="10", max_results=max_results)
        else:
            videos = crawler.get_most_viewed_videos(region_code=region, max_results=max_results)

        logger.info(f"[YouTube 采集] 获取到 {len(videos)} 条视频")

        if not videos:
            return {"message": "未获取到数据，请检查 YouTube API Key 是否有效或是否已启用 YouTube Data API v3", "count": 0, "api_key_configured": settings.YOUTUBE_API_ENABLED}

        saved = crawler.save_videos_to_db(videos, db)
        _run_post_crawl_analysis(db)
        return {"message": f"成功获取并保存 {len(saved)} 条 YouTube 视频", "count": len(saved)}
    except Exception as e:
        logger.error(f"[YouTube 采集] 失败: {e}")
        return {"message": f"YouTube 采集失败: {str(e)}", "count": 0}


@router.post("/tiktok")
def crawl_tiktok(
    type: str = Query("trending", description="采集类型: trending, hashtag, user"),
    keyword: str = Query("", description="关键词/标签"),
    max_results: int = Query(50, ge=1, le=50),
    db: Session = Depends(get_db),
):
    crawler = TikTokCrawler(use_free_first=True)
    videos = []

    if type == "hashtag" and keyword:
        videos = crawler.get_most_viewed_videos(hashtag=keyword, count=max_results)
    elif type == "user" and keyword:
        videos = crawler.search_viral_candidates(keyword=keyword, count=max_results)
    else:
        videos = crawler.get_trending_videos(count=max_results)

    if not videos:
        return {"message": "未获取到数据，TikTok 爬虫可能被反爬限制", "count": 0}

    saved = crawler.save_videos_to_db(videos, db)
    _run_post_crawl_analysis(db)
    return {"message": f"成功获取并保存 {len(saved)} 条 TikTok 视频", "count": len(saved)}


@router.post("/youtube/trending")
def crawl_youtube_trending(
    region_code: str = Query("US", description="区域代码，如 US, TW, JP"),
    max_results: int = Query(50, ge=1, le=50),
    db: Session = Depends(get_db),
):
    crawler = YouTubeCrawler()
    videos = crawler.get_trending_videos(region_code=region_code, max_results=max_results)
    if not videos:
        return {"message": "未获取到数据，请检查 YouTube API Key 是否配置", "count": 0}
    saved = crawler.save_videos_to_db(videos, db)
    _run_post_crawl_analysis(db)
    return {"message": f"成功获取并保存 {len(saved)} 条 YouTube 热门视频", "count": len(saved)}


@router.post("/youtube/most-viewed")
def crawl_youtube_most_viewed(
    query: str = Query("", description="搜索关键词"),
    region_code: str = Query("US", description="区域代码"),
    max_results: int = Query(50, ge=1, le=50),
    db: Session = Depends(get_db),
):
    crawler = YouTubeCrawler()
    videos = crawler.get_most_viewed_videos(query=query, region_code=region_code, max_results=max_results)
    if not videos:
        return {"message": "未获取到数据", "count": 0}
    saved = crawler.save_videos_to_db(videos, db)
    _run_post_crawl_analysis(db)
    return {"message": f"成功获取并保存 {len(saved)} 条 YouTube 高播放量视频", "count": len(saved)}


@router.post("/youtube/viral-candidates")
def crawl_youtube_viral(
    query: str = Query("", description="搜索关键词"),
    days: int = Query(7, ge=1, le=30, description="最近几天发布的视频"),
    max_results: int = Query(50, ge=1, le=50),
    db: Session = Depends(get_db),
):
    from datetime import datetime, timezone, timedelta
    published_after = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat() + "Z"

    crawler = YouTubeCrawler()
    videos = crawler.search_viral_candidates(query=query, published_after=published_after, max_results=max_results)
    if not videos:
        return {"message": "未获取到数据", "count": 0}
    saved = crawler.save_videos_to_db(videos, db)
    _run_post_crawl_analysis(db)
    return {"message": f"成功获取并保存 {len(saved)} 条 YouTube 爆红候选视频", "count": len(saved)}


@router.post("/tiktok/trending")
def crawl_tiktok_trending(
    count: int = Query(50, ge=1, le=50),
    db: Session = Depends(get_db),
):
    crawler = TikTokCrawler(use_free_first=True)
    videos = crawler.get_trending_videos(count=count)
    if not videos:
        return {"message": "未获取到数据，TikTok 爬虫可能被反爬限制", "count": 0}
    saved = crawler.save_videos_to_db(videos, db)
    _run_post_crawl_analysis(db)
    return {"message": f"成功获取并保存 {len(saved)} 条 TikTok 热门视频", "count": len(saved)}


@router.post("/tiktok/most-viewed")
def crawl_tiktok_most_viewed(
    hashtag: str = Query("", description="话题标签"),
    count: int = Query(50, ge=1, le=50),
    db: Session = Depends(get_db),
):
    crawler = TikTokCrawler(use_free_first=True)
    videos = crawler.get_most_viewed_videos(hashtag=hashtag, count=count)
    if not videos:
        return {"message": "未获取到数据", "count": 0}
    saved = crawler.save_videos_to_db(videos, db)
    _run_post_crawl_analysis(db)
    return {"message": f"成功获取并保存 {len(saved)} 条 TikTok 高播放量视频", "count": len(saved)}


@router.post("/tiktok/viral-candidates")
def crawl_tiktok_viral(
    keyword: str = Query("trending", description="搜索关键词"),
    count: int = Query(50, ge=1, le=50),
    db: Session = Depends(get_db),
):
    crawler = TikTokCrawler(use_free_first=True)
    videos = crawler.search_viral_candidates(keyword=keyword, count=count)
    if not videos:
        return {"message": "未获取到数据", "count": 0}
    saved = crawler.save_videos_to_db(videos, db)
    _run_post_crawl_analysis(db)
    return {"message": f"成功获取并保存 {len(saved)} 条 TikTok 爆红候选视频", "count": len(saved)}


@router.post("/all")
def crawl_all_platforms(
    region_code: str = Query("US", description="YouTube 区域代码"),
    db: Session = Depends(get_db),
):
    results = {}

    yt_crawler = YouTubeCrawler()
    yt_trending = yt_crawler.get_trending_videos(region_code=region_code)
    if yt_trending:
        yt_saved = yt_crawler.save_videos_to_db(yt_trending, db)
        results["youtube_trending"] = len(yt_saved)

    tt_crawler = TikTokCrawler(use_free_first=True)
    tt_trending = tt_crawler.get_trending_videos()
    if tt_trending:
        tt_saved = tt_crawler.save_videos_to_db(tt_trending, db)
        results["tiktok_trending"] = len(tt_saved)

    _run_post_crawl_analysis(db)

    return {"message": "全平台数据采集完成", "results": results}


@router.post("/reset-and-crawl")
def reset_and_crawl_real_data(db: Session = Depends(get_db)):
    from app.models.video import Video, VideoSnapshot, RevenueEstimate, ViralScore
    from app.config import settings
    
    db.query(ViralScore).delete()
    db.query(RevenueEstimate).delete()
    db.query(VideoSnapshot).delete()
    db.query(Video).delete()
    db.commit()
    
    results = {
        "youtube": 0,
        "tiktok": 0,
        "errors": []
    }
    
    if settings.YOUTUBE_API_ENABLED:
        try:
            yt_crawler = YouTubeCrawler()
            yt_videos = yt_crawler.get_trending_videos(region_code="US", max_results=50)
            if yt_videos:
                saved = yt_crawler.save_videos_to_db(yt_videos, db)
                results["youtube"] = len(saved)
        except Exception as e:
            results["errors"].append(f"YouTube: {str(e)}")
    
    try:
        tt_crawler = TikTokCrawler(tikhub_api_key=settings.TIKHUB_API_KEY, use_free_first=True)
        tt_videos = tt_crawler.get_trending_videos(count=50)
        if tt_videos:
            saved = tt_crawler.save_videos_to_db(tt_videos, db)
            results["tiktok"] = len(saved)
    except Exception as e:
        results["errors"].append(f"TikTok: {str(e)}")
    
    if results["youtube"] > 0 or results["tiktok"] > 0:
        _run_post_crawl_analysis(db)
    
    return {
        "message": "数据库已重置并重新采集",
        "youtube_api_enabled": settings.YOUTUBE_API_ENABLED,
        "tikhub_enabled": settings.TIKHUB_ENABLED,
        "results": results
    }


@router.post("/seed-demo")
def seed_demo_data(db: Session = Depends(get_db)):
    from app.demo.seed import generate_demo_data
    count = generate_demo_data(db)
    _run_post_crawl_analysis(db)
    return {"message": f"已生成 {count} 条演示数据", "count": count}
