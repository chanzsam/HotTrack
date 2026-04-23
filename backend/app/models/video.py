from sqlalchemy import Column, Integer, String, BigInteger, Float, DateTime, Text, Enum as SAEnum
from sqlalchemy.sql import func
from app.database import Base
import enum


class Platform(str, enum.Enum):
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(SAEnum(Platform), nullable=False, index=True)
    video_id = Column(String(100), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    channel_title = Column(String(200), nullable=True)
    channel_id = Column(String(100), nullable=True)
    published_at = Column(DateTime, nullable=True)
    thumbnail_url = Column(String(500), nullable=True)
    video_url = Column(String(500), nullable=False)
    duration = Column(String(50), nullable=True)
    category = Column(String(100), nullable=True)
    tags = Column(Text, nullable=True)

    view_count = Column(BigInteger, default=0)
    like_count = Column(BigInteger, default=0)
    comment_count = Column(BigInteger, default=0)
    share_count = Column(BigInteger, default=0)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        {"sqlite_autoincrement": True},
    )


class VideoSnapshot(Base):
    __tablename__ = "video_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, nullable=False, index=True)
    platform = Column(SAEnum(Platform), nullable=False, index=True)
    view_count = Column(BigInteger, default=0)
    like_count = Column(BigInteger, default=0)
    comment_count = Column(BigInteger, default=0)
    share_count = Column(BigInteger, default=0)
    snapshot_time = Column(DateTime, server_default=func.now())

    view_growth_rate = Column(Float, default=0.0)
    like_growth_rate = Column(Float, default=0.0)


class ViralRecord(Base):
    __tablename__ = "viral_records"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, nullable=False, index=True)
    platform = Column(SAEnum(Platform), nullable=False, index=True)
    hours_since_publish = Column(Float, nullable=False)
    view_count_at_time = Column(BigInteger, default=0)
    views_per_hour = Column(Float, default=0.0)
    viral_score = Column(Float, default=0.0)
    estimated_revenue = Column(Float, default=0.0)
    recorded_at = Column(DateTime, server_default=func.now())


class RevenueEstimate(Base):
    __tablename__ = "revenue_estimates"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, nullable=False, index=True)
    platform = Column(SAEnum(Platform), nullable=False, index=True)
    estimated_cpm = Column(Float, default=0.0)
    estimated_revenue_low = Column(Float, default=0.0)
    estimated_revenue_high = Column(Float, default=0.0)
    estimated_revenue_mid = Column(Float, default=0.0)
    revenue_currency = Column(String(10), default="USD")

    monetized_views = Column(BigInteger, default=0)
    ad_revenue = Column(Float, default=0.0)
    creator_share_amount = Column(Float, default=0.0)
    monetization_rate = Column(Float, default=0.0)
    creator_share_rate = Column(Float, default=0.0)

    calculated_at = Column(DateTime, server_default=func.now())
