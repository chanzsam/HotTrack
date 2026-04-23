from fastapi import APIRouter, Depends, Query, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.crawlers.youtube import YouTubeCrawler
from app.crawlers.tiktok import TikTokCrawler
from app.analyzers.viral import ViralAnalyzer
from app.analyzers.revenue import RevenueAnalyzer

router = APIRouter(prefix="/crawl", tags=["crawl"])


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
    try:
        viral_analyzer = ViralAnalyzer(db)
        viral_analyzer.calculate_viral_scores()
    except Exception:
        pass
    try:
        revenue_analyzer = RevenueAnalyzer(db)
        revenue_analyzer.batch_estimate_revenue()
    except Exception:
        pass


@router.post("/youtube")
def crawl_youtube(
    type: str = Query("popular", description="采集类型: popular, trending, category"),
    region: str = Query("US", description="区域代码"),
    max_results: int = Query(50, ge=1, le=50),
    db: Session = Depends(get_db),
):
    try:
        crawler = YouTubeCrawler()
        videos = []

        if type == "trending":
            videos = crawler.get_trending_videos(region_code=region, max_results=max_results)
        elif type == "category":
            videos = crawler.get_trending_videos(region_code=region, category_id="10", max_results=max_results)
        else:
            videos = crawler.get_most_viewed_videos(region_code=region, max_results=max_results)

        if not videos:
            return {"message": "未获取到数据，请检查 YouTube API Key 是否配置", "count": 0}

        saved = crawler.save_videos_to_db(videos, db)
        _run_post_crawl_analysis(db)
        return {"message": f"成功获取并保存 {len(saved)} 条 YouTube 视频", "count": len(saved)}
    except Exception as e:
        return {"message": f"YouTube 采集失败: {str(e)}", "count": 0}


@router.post("/tiktok")
def crawl_tiktok(
    type: str = Query("trending", description="采集类型: trending, hashtag, user"),
    keyword: str = Query("", description="关键词/标签"),
    max_results: int = Query(50, ge=1, le=50),
    db: Session = Depends(get_db),
):
    crawler = TikTokCrawler()
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
    crawler = TikTokCrawler()
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
    crawler = TikTokCrawler()
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
    crawler = TikTokCrawler()
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

    tt_crawler = TikTokCrawler()
    tt_trending = tt_crawler.get_trending_videos()
    if tt_trending:
        tt_saved = tt_crawler.save_videos_to_db(tt_trending, db)
        results["tiktok_trending"] = len(tt_saved)

    _run_post_crawl_analysis(db)

    return {"message": "全平台数据采集完成", "results": results}


@router.post("/seed-demo")
def seed_demo_data(db: Session = Depends(get_db)):
    from app.demo.seed import generate_demo_data
    count = generate_demo_data(db)
    _run_post_crawl_analysis(db)
    return {"message": f"已生成 {count} 条演示数据", "count": count}
