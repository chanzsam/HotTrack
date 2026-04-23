from datetime import datetime, timezone, timedelta
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.models.video import Video, VideoSnapshot, Platform, ViralRecord, RevenueEstimate


def _fmt_dt(dt):
    if dt is None:
        return None
    if hasattr(dt, 'tzinfo') and dt.tzinfo is not None:
        s = dt.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    else:
        s = dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    return s


class RankingAnalyzer:
    def __init__(self, db: Session):
        self.db = db

    def _attach_revenue(self, video: Video) -> dict:
        estimate = (
            self.db.query(RevenueEstimate)
            .filter(RevenueEstimate.video_id == video.id)
            .first()
        )
        if estimate:
            return {
                "estimated_cpm": estimate.estimated_cpm,
                "estimated_revenue_low": estimate.estimated_revenue_low,
                "estimated_revenue_mid": estimate.estimated_revenue_mid,
                "estimated_revenue_high": estimate.estimated_revenue_high,
                "revenue_currency": estimate.revenue_currency,
                "monetized_views": estimate.monetized_views,
                "ad_revenue": estimate.ad_revenue,
                "creator_share_amount": estimate.creator_share_amount,
                "monetization_rate": estimate.monetization_rate,
                "creator_share_rate": estimate.creator_share_rate,
            }
        return {
            "estimated_cpm": 0,
            "estimated_revenue_low": 0,
            "estimated_revenue_mid": 0,
            "estimated_revenue_high": 0,
            "revenue_currency": "USD",
            "monetized_views": 0,
            "ad_revenue": 0,
            "creator_share_amount": 0,
            "monetization_rate": 0,
            "creator_share_rate": 0,
        }

    def get_top_viewed_videos(
        self,
        platform: Optional[Platform] = None,
        limit: int = 50,
        category: Optional[str] = None,
    ) -> list[dict]:
        query = self.db.query(Video)

        if platform:
            query = query.filter(Video.platform == platform)
        if category:
            query = query.filter(Video.category == category)

        videos = query.order_by(desc(Video.view_count)).limit(limit).all()

        results = []
        for idx, v in enumerate(videos):
            revenue = self._attach_revenue(v)
            results.append({
                "rank": idx + 1,
                "id": v.id,
                "video_id": v.video_id,
                "platform": v.platform.value,
                "title": v.title,
                "channel_title": v.channel_title,
                "view_count": v.view_count,
                "like_count": v.like_count,
                "comment_count": v.comment_count,
                "share_count": v.share_count,
                "thumbnail_url": v.thumbnail_url,
                "video_url": v.video_url,
                "published_at": _fmt_dt(v.published_at),
                **revenue,
            })
        return results

    def get_top_liked_videos(
        self,
        platform: Optional[Platform] = None,
        limit: int = 50,
    ) -> list[dict]:
        query = self.db.query(Video)
        if platform:
            query = query.filter(Video.platform == platform)

        videos = query.order_by(desc(Video.like_count)).limit(limit).all()

        results = []
        for idx, v in enumerate(videos):
            revenue = self._attach_revenue(v)
            results.append({
                "rank": idx + 1,
                "id": v.id,
                "video_id": v.video_id,
                "platform": v.platform.value,
                "title": v.title,
                "channel_title": v.channel_title,
                "like_count": v.like_count,
                "view_count": v.view_count,
                "thumbnail_url": v.thumbnail_url,
                "video_url": v.video_url,
                **revenue,
            })
        return results

    def get_trending_videos(
        self,
        platform: Optional[Platform] = None,
        hours: int = 24,
        limit: int = 50,
    ) -> list[dict]:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

        subquery = (
            self.db.query(
                VideoSnapshot.video_id,
                func.max(VideoSnapshot.view_growth_rate).label("max_growth"),
            )
            .filter(VideoSnapshot.snapshot_time >= cutoff)
            .group_by(VideoSnapshot.video_id)
            .subquery()
        )

        query = (
            self.db.query(Video, subquery.c.max_growth)
            .join(subquery, Video.id == subquery.c.video_id)
            .filter(Video.published_at >= cutoff)
            .order_by(desc(subquery.c.max_growth))
        )

        if platform:
            query = query.filter(Video.platform == platform)

        results_raw = query.limit(limit).all()

        results = []
        for idx, (v, growth) in enumerate(results_raw):
            revenue = self._attach_revenue(v)
            results.append({
                "rank": idx + 1,
                "id": v.id,
                "video_id": v.video_id,
                "platform": v.platform.value,
                "title": v.title,
                "channel_title": v.channel_title,
                "view_count": v.view_count,
                "like_count": v.like_count,
                "growth_rate": growth,
                "thumbnail_url": v.thumbnail_url,
                "video_url": v.video_url,
                "published_at": _fmt_dt(v.published_at),
                **revenue,
            })
        return results

    def get_platform_stats(self) -> dict:
        youtube_total = self.db.query(func.count(Video.id)).filter(Video.platform == Platform.YOUTUBE).scalar() or 0
        tiktok_total = self.db.query(func.count(Video.id)).filter(Video.platform == Platform.TIKTOK).scalar() or 0

        youtube_views = self.db.query(func.sum(Video.view_count)).filter(Video.platform == Platform.YOUTUBE).scalar() or 0
        tiktok_views = self.db.query(func.sum(Video.view_count)).filter(Video.platform == Platform.TIKTOK).scalar() or 0

        youtube_revenue = self.db.query(func.sum(RevenueEstimate.estimated_revenue_mid)).filter(RevenueEstimate.platform == Platform.YOUTUBE).scalar() or 0
        tiktok_revenue = self.db.query(func.sum(RevenueEstimate.estimated_revenue_mid)).filter(RevenueEstimate.platform == Platform.TIKTOK).scalar() or 0

        return {
            "youtube": {
                "total_videos": youtube_total,
                "total_views": youtube_views,
                "total_estimated_revenue": round(youtube_revenue, 2),
            },
            "tiktok": {
                "total_videos": tiktok_total,
                "total_views": tiktok_views,
                "total_estimated_revenue": round(tiktok_revenue, 2),
            },
        }
