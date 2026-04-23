import logging
import os
from datetime import datetime, timezone, timedelta
from typing import Optional

import requests
from sqlalchemy.orm import Session

from app.config import settings
from app.models.video import Video, VideoSnapshot, Platform

logger = logging.getLogger(__name__)


class YouTubeCrawler:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.YOUTUBE_API_KEY
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self.proxies = self._get_proxies()
        logger.info(f"YouTubeCrawler 初始化: API Key 长度 = {len(self.api_key) if self.api_key else 0}")

    def _get_proxies(self) -> dict:
        proxy = os.environ.get("HTTP_PROXY") or os.environ.get("http_proxy") or os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
        if proxy:
            logger.info(f"使用代理: {proxy}")
            return {"http": proxy, "https": proxy}
        logger.info("不使用代理")
        return {}

    def _request(self, endpoint: str, params: dict) -> Optional[dict]:
        params["key"] = self.api_key
        url = f"{self.base_url}/{endpoint}"
        try:
            logger.info(f"YouTube API 请求: {endpoint}")
            logger.info(f"YouTube API Key 前缀: {self.api_key[:10] if self.api_key and len(self.api_key) > 10 else 'KEY_TOO_SHORT'}")
            logger.info(f"YouTube API Key 长度: {len(self.api_key) if self.api_key else 0}")
            
            resp = requests.get(url, params=params, proxies=self.proxies, timeout=30)
            logger.info(f"YouTube API 响应状态: {resp.status_code}")
            
            if resp.status_code != 200:
                logger.error(f"YouTube API 错误响应: {resp.text[:500]}")
                return None
            
            return resp.json()
        except requests.exceptions.Timeout:
            logger.error("YouTube API 请求超时")
            return None
        except requests.exceptions.ConnectionError as e:
            logger.error(f"YouTube API 连接错误: {e}")
            return None
        except Exception as e:
            logger.error(f"YouTube API 请求失败: {e}")
            return None

    def get_trending_videos(
        self, region_code: str = "US", category_id: Optional[str] = None, max_results: int = 50
    ) -> list[dict]:
        params = {
            "part": "snippet,contentDetails,statistics",
            "chart": "mostPopular",
            "regionCode": region_code,
            "maxResults": min(max_results, 50),
        }
        if category_id:
            params["videoCategoryId"] = category_id

        data = self._request("videos", params)
        if not data:
            return []

        videos = self._parse_video_list(data)
        logger.info(f"获取到 {len(videos)} 条 YouTube 热门视频 (区域: {region_code})")
        return videos

    def get_most_viewed_videos(
        self, query: str = "", region_code: str = "US", max_results: int = 50
    ) -> list[dict]:
        params = {
            "part": "snippet",
            "type": "video",
            "order": "viewCount",
            "q": query,
            "regionCode": region_code,
            "maxResults": min(max_results, 50),
        }
        data = self._request("search", params)
        if not data:
            return []

        video_ids = [item["id"]["videoId"] for item in data.get("items", [])]
        if not video_ids:
            return []

        stats_params = {
            "part": "snippet,contentDetails,statistics",
            "id": ",".join(video_ids),
        }
        stats_data = self._request("videos", stats_params)
        if not stats_data:
            return []

        videos = self._parse_video_list(stats_data)
        logger.info(f"获取到 {len(videos)} 条 YouTube 高播放量视频")
        return videos

    def search_viral_candidates(
        self, query: str = "", published_after: Optional[str] = None, max_results: int = 50
    ) -> list[dict]:
        if not published_after:
            published_after = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat() + "Z"

        params = {
            "part": "snippet",
            "type": "video",
            "order": "viewCount",
            "q": query,
            "maxResults": min(max_results, 50),
            "publishedAfter": published_after,
        }
        data = self._request("search", params)
        if not data:
            return []

        video_ids = [item["id"]["videoId"] for item in data.get("items", [])]
        if not video_ids:
            return []

        stats_params = {
            "part": "snippet,contentDetails,statistics",
            "id": ",".join(video_ids),
        }
        stats_data = self._request("videos", stats_params)
        if not stats_data:
            return []

        videos = self._parse_video_list(stats_data)
        logger.info(f"获取到 {len(videos)} 条 YouTube 爆红候选视频")
        return videos

    def get_video_details(self, video_id: str) -> Optional[dict]:
        params = {
            "part": "snippet,contentDetails,statistics",
            "id": video_id,
        }
        data = self._request("videos", params)
        if not data:
            return None

        items = data.get("items", [])
        if items:
            return self._parse_single_video(items[0])
        return None

    def get_channel_info(self, channel_id: str) -> Optional[dict]:
        params = {
            "part": "snippet,statistics",
            "id": channel_id,
        }
        data = self._request("channels", params)
        if not data:
            return None

        items = data.get("items", [])
        if items:
            item = items[0]
            return {
                "channel_id": item["id"],
                "title": item["snippet"]["title"],
                "subscriber_count": int(item["statistics"].get("subscriberCount", 0)),
                "video_count": int(item["statistics"].get("videoCount", 0)),
                "view_count": int(item["statistics"].get("viewCount", 0)),
            }
        return None

    def _parse_video_list(self, response: dict) -> list[dict]:
        videos = []
        for item in response.get("items", []):
            videos.append(self._parse_single_video(item))
        return videos

    def _parse_single_video(self, item: dict) -> dict:
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        content = item.get("contentDetails", {})

        published_at_str = snippet.get("publishedAt", "")
        published_at = None
        if published_at_str:
            try:
                published_at = datetime.fromisoformat(published_at_str.replace("Z", "+00:00"))
            except:
                pass

        return {
            "platform": Platform.YOUTUBE,
            "video_id": item["id"],
            "title": snippet.get("title", ""),
            "description": snippet.get("description", ""),
            "channel_title": snippet.get("channelTitle", ""),
            "channel_id": snippet.get("channelId", ""),
            "published_at": published_at,
            "thumbnail_url": self._get_best_thumbnail(snippet.get("thumbnails", {})),
            "video_url": f"https://www.youtube.com/watch?v={item['id']}",
            "duration": content.get("duration", ""),
            "category": snippet.get("categoryId", ""),
            "tags": ",".join(snippet.get("tags", [])),
            "view_count": int(stats.get("viewCount", 0)),
            "like_count": int(stats.get("likeCount", 0)),
            "comment_count": int(stats.get("commentCount", 0)),
            "share_count": 0,
        }

    @staticmethod
    def _get_best_thumbnail(thumbnails: dict) -> str:
        for quality in ["maxres", "high", "standard", "medium", "default"]:
            if quality in thumbnails:
                return thumbnails[quality]["url"]
        return ""

    def save_videos_to_db(self, videos: list[dict], db: Session) -> list[Video]:
        saved = []
        for video_data in videos:
            existing = (
                db.query(Video)
                .filter(Video.video_id == video_data["video_id"], Video.platform == Platform.YOUTUBE)
                .first()
            )

            if existing:
                old_views = existing.view_count
                old_likes = existing.like_count

                existing.view_count = video_data["view_count"]
                existing.like_count = video_data["like_count"]
                existing.comment_count = video_data["comment_count"]
                existing.title = video_data["title"]
                existing.updated_at = datetime.now(timezone.utc)

                snapshot = VideoSnapshot(
                    video_id=existing.id,
                    platform=Platform.YOUTUBE,
                    view_count=video_data["view_count"],
                    like_count=video_data["like_count"],
                    comment_count=video_data["comment_count"],
                    view_growth_rate=self._calc_growth_rate(old_views, video_data["view_count"]),
                    like_growth_rate=self._calc_growth_rate(old_likes, video_data["like_count"]),
                )
                db.add(snapshot)
                saved.append(existing)
            else:
                video = Video(**video_data)
                db.add(video)
                db.flush()

                snapshot = VideoSnapshot(
                    video_id=video.id,
                    platform=Platform.YOUTUBE,
                    view_count=video_data["view_count"],
                    like_count=video_data["like_count"],
                    comment_count=video_data["comment_count"],
                )
                db.add(snapshot)
                saved.append(video)

        db.commit()
        return saved

    @staticmethod
    def _calc_growth_rate(old: int, new: int) -> float:
        if old == 0:
            return 0.0
        return round((new - old) / old * 100, 4)
