from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.video import Video, RevenueEstimate, Platform


def _fmt_dt(dt):
    if dt is None:
        return None
    if hasattr(dt, 'tzinfo') and dt.tzinfo is not None:
        s = dt.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    else:
        s = dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    return s


YOUTUBE_CPM_LOW = 1.50
YOUTUBE_CPM_MID = 7.50
YOUTUBE_CPM_HIGH = 15.00

TIKTOK_CPM_LOW = 0.50
TIKTOK_CPM_MID = 2.00
TIKTOK_CPM_HIGH = 6.00

YOUTUBE_MONETIZATION_RATE = 0.55
YOUTUBE_CREATOR_SHARE = 0.55

TIKTOK_MONETIZATION_RATE = 0.30
TIKTOK_CREATOR_SHARE = 0.50


class RevenueAnalyzer:
    def __init__(self, db: Session):
        self.db = db

    def estimate_video_revenue(self, video: Video) -> RevenueEstimate:
        if video.platform == Platform.YOUTUBE:
            return self._estimate_youtube_revenue(video)
        else:
            return self._estimate_tiktok_revenue(video)

    def _estimate_youtube_revenue(self, video: Video) -> RevenueEstimate:
        monetized_views = int(video.view_count * YOUTUBE_MONETIZATION_RATE)
        total_ad_revenue = (monetized_views / 1000) * YOUTUBE_CPM_MID
        creator_share_amount = total_ad_revenue * YOUTUBE_CREATOR_SHARE

        revenue_low = (monetized_views / 1000) * YOUTUBE_CPM_LOW * YOUTUBE_CREATOR_SHARE
        revenue_mid = creator_share_amount
        revenue_high = (monetized_views / 1000) * YOUTUBE_CPM_HIGH * YOUTUBE_CREATOR_SHARE

        estimate = RevenueEstimate(
            video_id=video.id,
            platform=Platform.YOUTUBE,
            estimated_cpm=YOUTUBE_CPM_MID,
            estimated_revenue_low=round(revenue_low, 2),
            estimated_revenue_high=round(revenue_high, 2),
            estimated_revenue_mid=round(revenue_mid, 2),
            revenue_currency="USD",
            monetized_views=monetized_views,
            ad_revenue=round(total_ad_revenue, 2),
            creator_share_amount=round(creator_share_amount, 2),
            monetization_rate=YOUTUBE_MONETIZATION_RATE,
            creator_share_rate=YOUTUBE_CREATOR_SHARE,
        )
        self.db.add(estimate)
        self.db.commit()
        return estimate

    def _estimate_tiktok_revenue(self, video: Video) -> RevenueEstimate:
        monetized_views = int(video.view_count * TIKTOK_MONETIZATION_RATE)
        total_ad_revenue = (monetized_views / 1000) * TIKTOK_CPM_MID
        creator_share_amount = total_ad_revenue * TIKTOK_CREATOR_SHARE

        revenue_low = (monetized_views / 1000) * TIKTOK_CPM_LOW * TIKTOK_CREATOR_SHARE
        revenue_mid = creator_share_amount
        revenue_high = (monetized_views / 1000) * TIKTOK_CPM_HIGH * TIKTOK_CREATOR_SHARE

        estimate = RevenueEstimate(
            video_id=video.id,
            platform=Platform.TIKTOK,
            estimated_cpm=TIKTOK_CPM_MID,
            estimated_revenue_low=round(revenue_low, 2),
            estimated_revenue_high=round(revenue_high, 2),
            estimated_revenue_mid=round(revenue_mid, 2),
            revenue_currency="USD",
            monetized_views=monetized_views,
            ad_revenue=round(total_ad_revenue, 2),
            creator_share_amount=round(creator_share_amount, 2),
            monetization_rate=TIKTOK_MONETIZATION_RATE,
            creator_share_rate=TIKTOK_CREATOR_SHARE,
        )
        self.db.add(estimate)
        self.db.commit()
        return estimate

    def get_top_revenue_videos(
        self,
        platform: Optional[Platform] = None,
        limit: int = 50,
    ) -> list[dict]:
        query = (
            self.db.query(Video, RevenueEstimate)
            .join(RevenueEstimate, Video.id == RevenueEstimate.video_id)
            .order_by(desc(RevenueEstimate.estimated_revenue_mid))
        )

        if platform:
            query = query.filter(Video.platform == platform)

        results = query.limit(limit).all()

        return [
            {
                "rank": idx + 1,
                "id": v.id,
                "video_id": v.video_id,
                "platform": v.platform.value,
                "title": v.title,
                "channel_title": v.channel_title,
                "view_count": v.view_count,
                "estimated_cpm": r.estimated_cpm,
                "estimated_revenue_low": r.estimated_revenue_low,
                "estimated_revenue_mid": r.estimated_revenue_mid,
                "estimated_revenue_high": r.estimated_revenue_high,
                "revenue_currency": r.revenue_currency,
                "monetized_views": r.monetized_views,
                "ad_revenue": r.ad_revenue,
                "creator_share_amount": r.creator_share_amount,
                "monetization_rate": r.monetization_rate,
                "creator_share_rate": r.creator_share_rate,
                "thumbnail_url": v.thumbnail_url,
                "video_url": v.video_url,
                "published_at": _fmt_dt(v.published_at),
            }
            for idx, (v, r) in enumerate(results)
        ]

    def batch_estimate_revenue(self, platform: Optional[Platform] = None) -> int:
        existing_ids = set(
            row[0] for row in self.db.query(RevenueEstimate.video_id).all()
        )

        query = self.db.query(Video)
        if platform:
            query = query.filter(Video.platform == platform)

        videos = query.filter(~Video.id.in_(existing_ids) if existing_ids else True).all()

        count = 0
        for video in videos:
            if video.view_count > 0:
                self.estimate_video_revenue(video)
                count += 1

        return count

    def get_revenue_for_video(self, video_id: int) -> Optional[dict]:
        estimate = self.db.query(RevenueEstimate).filter(RevenueEstimate.video_id == video_id).first()
        if not estimate:
            video = self.db.query(Video).filter(Video.id == video_id).first()
            if video and video.view_count > 0:
                estimate = self.estimate_video_revenue(video)
            else:
                return None
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
