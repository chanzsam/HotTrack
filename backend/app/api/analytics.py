from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.video import Platform
from app.analyzers.viral import ViralAnalyzer
from app.analyzers.revenue import RevenueAnalyzer

router = APIRouter(prefix="/analytics", tags=["analytics"])


def _parse_platform(platform: Optional[str]) -> Optional[Platform]:
    if not platform:
        return None
    try:
        return Platform(platform)
    except ValueError:
        valid = [p.value for p in Platform]
        raise HTTPException(status_code=422, detail=f"无效的平台参数: {platform}，有效值: {valid}")


@router.get("/viral")
def get_viral_videos(
    platform: Optional[str] = Query(None, description="平台筛选: youtube 或 tiktok"),
    limit: int = Query(50, ge=1, le=200),
    min_views: int = Query(1000, ge=0, description="最低播放量"),
    hours: int = Query(720, ge=1, le=2160, description="发布时间范围（小时）"),
    db: Session = Depends(get_db),
):
    p = _parse_platform(platform)
    analyzer = ViralAnalyzer(db)
    return analyzer.get_fastest_growing_videos(platform=p, limit=limit, min_views=min_views, hours_threshold=hours)


@router.post("/viral/calculate")
def calculate_viral_scores(
    hours_threshold: float = Query(168, ge=1, le=720, description="最大发布时长（小时）"),
    db: Session = Depends(get_db),
):
    analyzer = ViralAnalyzer(db)
    records = analyzer.calculate_viral_scores(hours_threshold=hours_threshold)
    return {"message": f"已计算 {len(records)} 条视频的爆红指数", "count": len(records)}


@router.get("/revenue")
def get_revenue_ranking(
    platform: Optional[str] = Query(None, description="平台筛选: youtube 或 tiktok"),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    p = _parse_platform(platform)
    analyzer = RevenueAnalyzer(db)
    return analyzer.get_top_revenue_videos(platform=p, limit=limit)


@router.get("/revenue/ranking")
def get_revenue_ranking_alias(
    platform: Optional[str] = Query(None, description="平台筛选: youtube 或 tiktok"),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    p = _parse_platform(platform)
    analyzer = RevenueAnalyzer(db)
    return analyzer.get_top_revenue_videos(platform=p, limit=limit)


@router.post("/revenue/calculate")
def calculate_revenue(
    platform: Optional[str] = Query(None, description="平台筛选: youtube 或 tiktok"),
    db: Session = Depends(get_db),
):
    p = _parse_platform(platform)
    analyzer = RevenueAnalyzer(db)
    count = analyzer.batch_estimate_revenue(platform=p)
    return {"message": f"已估算 {count} 条视频的收入", "count": count}
