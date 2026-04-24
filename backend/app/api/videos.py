from typing import Optional
import logging
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.video import Platform, Video, VideoSnapshot, ViralRecord, RevenueEstimate
from app.analyzers.ranking import RankingAnalyzer
from app.crawlers.youtube import YouTubeCrawler

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/videos", tags=["videos"])


def _parse_platform(platform: Optional[str]) -> Optional[Platform]:
    if not platform:
        return None
    try:
        return Platform(platform)
    except ValueError:
        valid = [p.value for p in Platform]
        raise HTTPException(status_code=422, detail=f"无效的平台参数: {platform}，有效值: {valid}")


@router.get("/top-viewed")
def get_top_viewed(
    platform: Optional[str] = Query(None, description="平台筛选: youtube 或 tiktok"),
    limit: int = Query(50, ge=1, le=200),
    category: Optional[str] = Query(None, description="分类筛选"),
    db: Session = Depends(get_db),
):
    p = _parse_platform(platform)
    analyzer = RankingAnalyzer(db)
    return analyzer.get_top_viewed_videos(platform=p, limit=limit, category=category)


@router.get("/top-liked")
def get_top_liked(
    platform: Optional[str] = Query(None, description="平台筛选: youtube 或 tiktok"),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    p = _parse_platform(platform)
    analyzer = RankingAnalyzer(db)
    return analyzer.get_top_liked_videos(platform=p, limit=limit)


@router.get("/trending")
def get_trending(
    platform: Optional[str] = Query(None, description="平台筛选: youtube 或 tiktok"),
    hours: int = Query(24, ge=1, le=720, description="时间范围（小时）"),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    p = _parse_platform(platform)
    analyzer = RankingAnalyzer(db)
    return analyzer.get_trending_videos(platform=p, hours=hours, limit=limit)


@router.get("/stats")
def get_platform_stats(db: Session = Depends(get_db)):
    analyzer = RankingAnalyzer(db)
    return analyzer.get_platform_stats()


@router.post("/cleanup-invalid")
def cleanup_invalid_videos(
    platform: Optional[str] = Query(None, description="平台筛选: youtube 或 tiktok"),
    dry_run: bool = Query(False, description="仅检测不删除"),
    db: Session = Depends(get_db),
):
    p = _parse_platform(platform)
    
    query = db.query(Video)
    if p:
        query = query.filter(Video.platform == p)
    
    videos = query.all()
    crawler = YouTubeCrawler()
    
    valid_videos = []
    invalid_videos = []
    
    for video in videos:
        is_valid = True
        invalid_reason = ""
        
        try:
            if video.platform == Platform.YOUTUBE:
                details = crawler.get_video_details(video.video_id)
                if not details:
                    is_valid = False
                    invalid_reason = "视频链接失效"
                elif details.get("view_count", 0) == 0 and details.get("like_count", 0) == 0:
                    is_valid = False
                    invalid_reason = "数据为空(播放量=0,点赞=0)"
            
            if is_valid and video.view_count == 0 and video.like_count == 0:
                is_valid = False
                invalid_reason = "本地数据为空(播放量=0,点赞=0)"
            
            if is_valid and not video.thumbnail_url:
                is_valid = False
                invalid_reason = "缩略图缺失"
                
        except Exception as e:
            logger.error(f"检测视频 {video.video_id} 失败: {e}")
            is_valid = False
            invalid_reason = f"检测异常: {str(e)[:50]}"
        
        if is_valid:
            valid_videos.append(video.id)
        else:
            invalid_videos.append({
                "id": video.id,
                "video_id": video.video_id,
                "platform": video.platform.value,
                "title": video.title,
                "reason": invalid_reason,
            })
    
    if not dry_run and invalid_videos:
        for inv in invalid_videos:
            db.query(VideoSnapshot).filter(VideoSnapshot.video_id == inv["id"]).delete()
            db.query(ViralRecord).filter(ViralRecord.video_id == inv["id"]).delete()
            db.query(RevenueEstimate).filter(RevenueEstimate.video_id == inv["id"]).delete()
            db.query(Video).filter(Video.id == inv["id"]).delete()
        db.commit()
    
    return {
        "total_checked": len(videos),
        "valid_count": len(valid_videos),
        "invalid_count": len(invalid_videos),
        "invalid_videos": invalid_videos[:20],
        "dry_run": dry_run,
        "deleted": not dry_run and len(invalid_videos) > 0,
    }
