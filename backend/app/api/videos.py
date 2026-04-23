from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.video import Platform
from app.analyzers.ranking import RankingAnalyzer

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
