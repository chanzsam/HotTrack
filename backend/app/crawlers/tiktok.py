import logging
import re
import json
import os
from datetime import datetime, timezone
from typing import Optional

import requests
from sqlalchemy.orm import Session

from app.models.video import Video, VideoSnapshot, Platform

logger = logging.getLogger(__name__)


class TikTokCrawler:
    def __init__(self, tikhub_api_key: Optional[str] = None):
        self.tikhub_api_key = tikhub_api_key or os.environ.get("TIKHUB_API_KEY")
        self.tikhub_base_url = "https://api.tikhub.io"
        
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.tiktok.com/",
        })

    def get_trending_videos(self, count: int = 50) -> list[dict]:
        if self.tikhub_api_key:
            videos = self._get_via_tikhub("trending", count)
            if videos:
                return videos
        
        return self._get_via_scraper("trending", count)

    def get_most_viewed_videos(self, hashtag: str = "", count: int = 50) -> list[dict]:
        if self.tikhub_api_key:
            videos = self._get_via_tikhub("popular", count, hashtag=hashtag)
            if videos:
                return videos
        
        return self._get_via_scraper(hashtag or "popular", count)

    def search_viral_candidates(self, keyword: str = "", count: int = 50) -> list[dict]:
        if self.tikhub_api_key:
            videos = self._get_via_tikhub("search", count, keyword=keyword or "trending")
            if videos:
                return videos
        
        return self._get_via_scraper(keyword or "viral", count)

    def _get_via_tikhub(self, method: str, count: int, keyword: str = "", hashtag: str = "") -> list[dict]:
        headers = {
            "Authorization": f"Bearer {self.tikhub_api_key}",
            "Content-Type": "application/json"
        }
        
        endpoints = [
            {
                "url": f"{self.tikhub_base_url}/api/v1/tiktok/web/fetch_hashtag_video_list",
                "params": {"hashtagName": "fyp", "count": min(count, 30), "cursor": 0},
            },
            {
                "url": f"{self.tikhub_base_url}/api/v1/tiktok/web/fetch_general_search",
                "params": {"keyword": keyword or hashtag or "trending", "count": min(count, 30), "offset": 0},
            },
        ]
        
        for endpoint in endpoints:
            try:
                logger.info(f"[TikHub] 尝试端点: {endpoint['url']}")
                resp = requests.get(endpoint["url"], headers=headers, params=endpoint["params"], timeout=30)
                
                logger.info(f"[TikHub] 响应状态: {resp.status_code}")
                
                if resp.status_code == 200:
                    data = resp.json()
                    logger.info(f"[TikHub] 响应数据键: {list(data.keys())}")
                    
                    videos = self._parse_tikhub_response_v2(data)
                    if videos:
                        logger.info(f"[TikHub] 成功获取 {len(videos)} 条 TikTok 视频")
                        return videos
                    else:
                        logger.warning(f"[TikHub] 端点返回空数据")
                else:
                    logger.warning(f"[TikHub] API 请求失败: {resp.status_code} - {resp.text[:200]}")
                    
            except Exception as e:
                logger.error(f"[TikHub] 请求出错: {e}")
        
        logger.error("[TikHub] 所有端点都失败")
        return []

    def _parse_tikhub_response_v2(self, data: dict) -> list[dict]:
        videos = []
        
        items = []
        
        if "data" in data:
            inner = data["data"]
            
            if isinstance(inner, dict):
                if "aweme_list" in inner:
                    items = inner["aweme_list"]
                elif "data" in inner:
                    for item in inner["data"]:
                        if item.get("type") == 1:
                            aweme = item.get("item", item.get("aweme", {}))
                            if aweme and aweme.get("id"):
                                items.append(aweme)
                elif "video_list" in inner:
                    items = inner["video_list"]
                elif "itemList" in inner:
                    items = inner["itemList"]
            elif isinstance(inner, list):
                items = inner
        
        logger.info(f"[TikHub] 找到 {len(items)} 个视频项")
        
        for item in items:
            try:
                video = self._parse_tiktok_item(item)
                if video and video.get("video_id"):
                    videos.append(video)
            except Exception as e:
                logger.debug(f"解析视频失败: {e}")
                continue
        
        return videos

    def _parse_tikhub_response(self, data: dict, method: str) -> list[dict]:
        videos = []
        
        if method == "trending":
            items = data.get("data", {}).get("aweme_list", [])
        else:
            items = []
            raw_data = data.get("data", {}).get("data", [])
            for item in raw_data:
                if item.get("type") == 1:
                    aweme = item.get("item", item.get("aweme", {}))
                    if aweme and aweme.get("id"):
                        items.append(aweme)
        
        for item in items:
            try:
                video = self._parse_tiktok_item(item)
                videos.append(video)
            except Exception as e:
                logger.debug(f"解析视频失败: {e}")
                continue
        
        return videos

    def _get_via_scraper(self, keyword: str, count: int) -> list[dict]:
        logger.info(f"[免费爬虫] 尝试抓取 TikTok '{keyword}' 视频...")
        
        methods = [
            self._scrape_via_api,
            self._scrape_via_page,
        ]
        
        for method in methods:
            try:
                videos = method(keyword, count)
                if videos:
                    logger.info(f"[免费爬虫] 获取到 {len(videos)} 条视频")
                    return videos
            except Exception as e:
                logger.debug(f"爬虫方法失败: {e}")
                continue
        
        return []

    def _scrape_via_api(self, keyword: str, count: int) -> list[dict]:
        url = "https://www.tiktok.com/api/discover/item_list"
        params = {
            "aid": "1988",
            "count": min(count, 50),
            "itemType": "0",
        }
        
        resp = self.session.get(url, params=params, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            items = data.get("itemList", [])
            if items:
                return [self._parse_tiktok_item(item) for item in items]
        
        return []

    def _scrape_via_page(self, keyword: str, count: int) -> list[dict]:
        url = f"https://www.tiktok.com/tag/{keyword}" if keyword != "trending" else "https://www.tiktok.com/trending"
        
        resp = self.session.get(url, timeout=30)
        if resp.status_code != 200:
            return []
        
        match = re.search(
            r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">(.*?)</script>',
            resp.text,
        )
        if not match:
            return []
        
        data = json.loads(match.group(1))
        items = []
        
        for scope_key, scope_data in data.items():
            if isinstance(scope_data, dict):
                for sub_key, sub_data in scope_data.items():
                    if isinstance(sub_data, dict):
                        item_list = sub_data.get("itemList", sub_data.get("list", []))
                        if isinstance(item_list, list):
                            items.extend(item_list)
        
        if items:
            return [self._parse_tiktok_item(item) for item in items[:count]]
        
        return []

    def _parse_tiktok_item(self, item: dict) -> dict:
        video_id = item.get("id", item.get("aweme_id", ""))
        desc = item.get("desc", "")
        author = item.get("author", {})
        stats = item.get("stats", item.get("statistics", item.get("statsV2", {})))
        video_info = item.get("video", {})

        publish_time = item.get("createTime", item.get("create_time", ""))
        try:
            published_at = datetime.fromtimestamp(int(publish_time), tz=timezone.utc)
        except (ValueError, TypeError):
            published_at = datetime.now(timezone.utc)

        cover = video_info.get("cover", video_info.get("originCover", video_info.get("play_addr", {})))
        if isinstance(cover, dict):
            cover = cover.get("url_list", [""])[0] if cover.get("url_list") else ""
        
        def get_stat(key: str) -> int:
            val = stats.get(key, stats.get(key[0].upper() + key[1:], 0))
            return int(val) if val else 0

        return {
            "platform": Platform.TIKTOK,
            "video_id": str(video_id),
            "title": desc[:500] if desc else f"TikTok Video {video_id}",
            "description": desc,
            "channel_title": author.get("uniqueId", author.get("unique_id", author.get("nickname", ""))),
            "channel_id": str(author.get("id", author.get("uid", ""))),
            "published_at": published_at,
            "thumbnail_url": cover,
            "video_url": f"https://www.tiktok.com/@{author.get('uniqueId', author.get('unique_id', ''))}/video/{video_id}",
            "duration": str(video_info.get("duration", 0)),
            "category": "",
            "tags": ",".join(
                tag.get("name", tag.get("hashtagName", "")) 
                for tag in item.get("textExtra", item.get("text_extra", [])) 
                if tag.get("name") or tag.get("hashtagName")
            ),
            "view_count": get_stat("playCount"),
            "like_count": get_stat("diggCount"),
            "comment_count": get_stat("commentCount"),
            "share_count": get_stat("shareCount"),
        }

    def save_videos_to_db(self, videos: list[dict], db: Session) -> list[Video]:
        saved = []
        for video_data in videos:
            existing = (
                db.query(Video)
                .filter(Video.video_id == video_data["video_id"], Video.platform == Platform.TIKTOK)
                .first()
            )

            if existing:
                old_views = existing.view_count
                old_likes = existing.like_count

                existing.view_count = video_data["view_count"]
                existing.like_count = video_data["like_count"]
                existing.comment_count = video_data["comment_count"]
                existing.share_count = video_data["share_count"]
                existing.updated_at = datetime.now(timezone.utc)

                snapshot = VideoSnapshot(
                    video_id=existing.id,
                    platform=Platform.TIKTOK,
                    view_count=video_data["view_count"],
                    like_count=video_data["like_count"],
                    comment_count=video_data["comment_count"],
                    share_count=video_data["share_count"],
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
                    platform=Platform.TIKTOK,
                    view_count=video_data["view_count"],
                    like_count=video_data["like_count"],
                    comment_count=video_data["comment_count"],
                    share_count=video_data["share_count"],
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
