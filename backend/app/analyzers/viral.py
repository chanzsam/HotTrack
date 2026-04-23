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


class ViralAnalyzer:
    def __init__(self, db: Session):
        self.db = db

    def _attach_revenue(self, video_id: int) -> dict:
        estimate = (
            self.db.query(RevenueEstimate)
            .filter(RevenueEstimate.video_id == video_id)
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

    def calculate_viral_scores(self, hours_threshold: float = 168) -> list[ViralRecord]:
        videos = self.db.query(Video).all()
        records = []

        for video in videos:
            if not video.published_at:
                continue

            now = datetime.now(timezone.utc)
            if hasattr(video.published_at, 'tzinfo') and video.published_at.tzinfo is None:
                pub_time = video.published_at.replace(tzinfo=timezone.utc)
            else:
                pub_time = video.published_at

            hours_since_publish = (now - pub_time).total_seconds() / 3600

            if hours_since_publish <= 0 or hours_since_publish > hours_threshold:
                continue

            views_per_hour = video.view_count / hours_since_publish if hours_since_publish > 0 else 0

            snapshots = (
                self.db.query(VideoSnapshot)
                .filter(VideoSnapshot.video_id == video.id)
                .order_by(desc(VideoSnapshot.snapshot_time))
                .limit(2)
                .all()
            )

            recent_growth = 0.0
            if len(snapshots) >= 2:
                latest = snapshots[0]
                previous = snapshots[1]
                if previous.view_count > 0:
                    recent_growth = (latest.view_count - previous.view_count) / previous.view_count * 100

            viral_score = self._compute_viral_score(
                views_per_hour=views_per_hour,
                hours_since_publish=hours_since_publish,
                recent_growth_rate=recent_growth,
                total_views=video.view_count,
            )

            record = ViralRecord(
                video_id=video.id,
                platform=video.platform,
                hours_since_publish=round(hours_since_publish, 2),
                view_count_at_time=video.view_count,
                views_per_hour=round(views_per_hour, 2),
                viral_score=round(viral_score, 4),
            )
            self.db.add(record)
            records.append(record)

        self.db.commit()
        return records

    def get_fastest_growing_videos(
        self,
        platform: Optional[Platform] = None,
        limit: int = 50,
        min_views: int = 1000,
        hours_threshold: float = 720,
    ) -> list[dict]:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours_threshold)

        subquery = (
            self.db.query(
                ViralRecord.video_id,
                func.max(ViralRecord.viral_score).label("max_score"),
                func.max(ViralRecord.views_per_hour).label("max_vph"),
                func.max(ViralRecord.hours_since_publish).label("hours"),
            )
            .group_by(ViralRecord.video_id)
            .subquery()
        )

        query = (
            self.db.query(Video, subquery.c.max_score, subquery.c.max_vph, subquery.c.hours)
            .join(subquery, Video.id == subquery.c.video_id)
            .filter(Video.view_count >= min_views)
            .filter(Video.published_at >= cutoff)
            .order_by(desc(subquery.c.max_score))
        )

        if platform:
            query = query.filter(Video.platform == platform)

        results = query.limit(limit).all()

        output = []
        for idx, (v, score, vph, hours) in enumerate(results):
            revenue = self._attach_revenue(v.id)
            output.append({
                "rank": idx + 1,
                "id": v.id,
                "video_id": v.video_id,
                "platform": v.platform.value,
                "title": v.title,
                "channel_title": v.channel_title,
                "view_count": v.view_count,
                "like_count": v.like_count,
                "viral_score": score,
                "viral_speed": vph,
                "hours_since_publish": hours,
                "thumbnail_url": v.thumbnail_url,
                "video_url": v.video_url,
                "published_at": _fmt_dt(v.published_at),
                **revenue,
            })
        return output

    @staticmethod
    def _compute_viral_score(
        views_per_hour: float,
        hours_since_publish: float,
        recent_growth_rate: float,
        total_views: int,
    ) -> float:
        vph_score = min(views_per_hour / 10000, 10) * 30
        recency_bonus = max(0, (168 - hours_since_publish) / 168) * 20
        growth_score = min(recent_growth_rate / 50, 10) * 30
        volume_score = min(total_views / 1000000, 10) * 20
        return vph_score + recency_bonus + growth_score + volume_score
