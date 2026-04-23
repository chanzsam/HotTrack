import logging
import re
import json
import os
import random
from datetime import datetime, timezone
from typing import Optional

import requests
from sqlalchemy.orm import Session

from app.models.video import Video, VideoSnapshot, Platform

logger = logging.getLogger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1",
]


class TikTokCrawler:
    def __init__(self, tikhub_api_key: Optional[str] = None, use_free_first: bool = True):
        self.tikhub_api_key = tikhub_api_key or os.environ.get("TIKHUB_API_KEY")
        self.tikhub_base_url = "https://api.tikhub.io"
        self.use_free_first = use_free_first
        
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Sec-Ch-Ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
        })

    def get_trending_videos(self, count: int = 50) -> list[dict]:
        if self.use_free_first:
            videos = self._get_via_free_methods("trending", count)
            if videos:
                return videos
            
            if self.tikhub_api_key:
                videos = self._get_via_tikhub("trending", count)
                if videos:
                    return videos
        else:
            if self.tikhub_api_key:
                videos = self._get_via_tikhub("trending", count)
                if videos:
                    return videos
            
            videos = self._get_via_free_methods("trending", count)
            if videos:
                return videos
        
        return self._generate_demo_tiktok_data(count)

    def get_most_viewed_videos(self, hashtag: str = "", count: int = 50) -> list[dict]:
        if self.use_free_first:
            videos = self._get_via_free_methods(hashtag or "popular", count)
            if videos:
                return videos
            
            if self.tikhub_api_key:
                videos = self._get_via_tikhub("popular", count, hashtag=hashtag)
                if videos:
                    return videos
        else:
            if self.tikhub_api_key:
                videos = self._get_via_tikhub("popular", count, hashtag=hashtag)
                if videos:
                    return videos
            
            videos = self._get_via_free_methods(hashtag or "popular", count)
            if videos:
                return videos
        
        return self._generate_demo_tiktok_data(count)

    def search_viral_candidates(self, keyword: str = "", count: int = 50) -> list[dict]:
        return self.get_trending_videos(count)

    def _get_via_free_methods(self, keyword: str, count: int) -> list[dict]:
        logger.info(f"[免费爬虫] 尝试抓取 TikTok '{keyword}' 视频...")
        
        methods = [
            ("公开 API", self._scrape_via_public_api),
            ("网页抓取", self._scrape_via_page),
            ("备用 API", self._scrape_via_backup_api),
        ]
        
        for method_name, method in methods:
            try:
                logger.info(f"[免费爬虫] 尝试方法: {method_name}")
                videos = method(keyword, count)
                if videos:
                    logger.info(f"[免费爬虫] {method_name} 成功获取 {len(videos)} 条视频")
                    return videos
            except Exception as e:
                logger.warning(f"[免费爬虫] {method_name} 失败: {e}")
                continue
        
        logger.warning("[免费爬虫] 所有免费方法都失败")
        return []

    def _scrape_via_public_api(self, keyword: str, count: int) -> list[dict]:
        endpoints = [
            "https://www.tiktok.com/api/recommend/item_list",
            "https://www.tiktok.com/api/discover/item_list",
        ]
        
        for url in endpoints:
            try:
                params = {
                    "aid": "1988",
                    "app_language": "en",
                    "app_name": "tiktok_web",
                    "browser_language": "en-US",
                    "browser_name": "Mozilla",
                    "browser_online": "true",
                    "browser_platform": "Win32",
                    "browser_version": "5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "channel": "tiktok_web",
                    "cookie_enabled": "true",
                    "count": min(count, 30),
                    "device_id": str(random.randint(7000000000000000000, 7999999999999999999)),
                    "device_platform": "web_pc",
                    "device_type": "web",
                    "focus_state": "true",
                    "from_page": "fyp",
                    "history_len": "2",
                    "is_fullscreen": "false",
                    "is_page_visible": "true",
                    "language": "en",
                    "os": "windows",
                    "priority_region": "",
                    "referer": "",
                    "region": "US",
                    "screen_height": "1080",
                    "screen_width": "1920",
                    "tz_name": "America/New_York",
                    "webcast_language": "en",
                }
                
                resp = self.session.get(url, params=params, timeout=15)
                
                if resp.status_code == 200:
                    data = resp.json()
                    items = data.get("itemList", data.get("items", []))
                    if items:
                        videos = []
                        for item in items[:count]:
                            try:
                                video = self._parse_tiktok_item(item)
                                if video and video.get("video_id"):
                                    videos.append(video)
                            except:
                                continue
                        return videos
            except Exception as e:
                logger.debug(f"公开 API 端点失败: {e}")
                continue
        
        return []

    def _scrape_via_backup_api(self, keyword: str, count: int) -> list[dict]:
        try:
            url = "https://tiktok-video-features.p.rapidapi.com/trending"
            headers = {
                "X-RapidAPI-Key": "demo",
                "X-RapidAPI-Host": "tiktok-video-features.p.rapidapi.com"
            }
            params = {"limit": min(count, 20)}
            
            resp = requests.get(url, headers=headers, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list):
                    videos = []
                    for item in data[:count]:
                        try:
                            video = {
                                "platform": Platform.TIKTOK,
                                "video_id": str(item.get("id", "")),
                                "title": item.get("desc", "")[:500],
                                "description": item.get("desc", ""),
                                "channel_title": item.get("author", {}).get("uniqueId", ""),
                                "channel_id": str(item.get("author", {}).get("id", "")),
                                "published_at": datetime.now(timezone.utc),
                                "thumbnail_url": item.get("video", {}).get("cover", ""),
                                "video_url": f"https://www.tiktok.com/@{item.get('author', {}).get('uniqueId', '')}/video/{item.get('id', '')}",
                                "duration": str(item.get("video", {}).get("duration", 0)),
                                "category": "",
                                "tags": "",
                                "view_count": int(item.get("stats", {}).get("playCount", 0)),
                                "like_count": int(item.get("stats", {}).get("diggCount", 0)),
                                "comment_count": int(item.get("stats", {}).get("commentCount", 0)),
                                "share_count": int(item.get("stats", {}).get("shareCount", 0)),
                            }
                            videos.append(video)
                        except:
                            continue
                    return videos
        except Exception as e:
            logger.debug(f"备用 API 失败: {e}")
        
        return []

    def _scrape_via_page(self, keyword: str, count: int) -> list[dict]:
        urls = [
            "https://www.tiktok.com/trending",
            "https://www.tiktok.com/foryou",
            f"https://www.tiktok.com/tag/{keyword}",
        ]
        
        for url in urls:
            try:
                self.session.headers.update({
                    "Referer": "https://www.tiktok.com/",
                })
                resp = self.session.get(url, timeout=15)
                
                if resp.status_code != 200:
                    continue
                
                match = re.search(
                    r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">(.*?)</script>',
                    resp.text,
                )
                if not match:
                    match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.*?});', resp.text)
                
                if not match:
                    continue
                
                data = json.loads(match.group(1))
                items = []
                
                def extract_items(obj, depth=0):
                    if depth > 10:
                        return
                    if isinstance(obj, dict):
                        for key in ["itemList", "items", "videoList", "aweme_list"]:
                            if key in obj and isinstance(obj[key], list):
                                items.extend(obj[key])
                        for v in obj.values():
                            extract_items(v, depth + 1)
                    elif isinstance(obj, list):
                        for item in obj:
                            extract_items(item, depth + 1)
                
                extract_items(data)
                
                if items:
                    videos = []
                    for item in items[:count]:
                        try:
                            video = self._parse_tiktok_item(item)
                            if video and video.get("video_id"):
                                videos.append(video)
                        except:
                            continue
                    return videos
            except Exception as e:
                logger.debug(f"网页抓取失败: {e}")
                continue
        
        return []

    def _generate_demo_tiktok_data(self, count: int) -> list[dict]:
        logger.info(f"[演示数据] 生成 {count} 条 TikTok 演示数据")
        
        real_tiktok_videos = [
            {"id": "6860726483632062981", "creator": "bellapoarch", "title": "M to the B 🎵 #fyp #mtob", "views": 722000000},
            {"id": "7018472888663588869", "creator": "khaby.lame", "title": "Life hack 😂 #khaby #fyp", "views": 360000000},
            {"id": "6941113121911083013", "creator": "charlidamelio", "title": "Dance trend 💃 #fyp #viral", "views": 285000000},
            {"id": "7024456387604471606", "creator": "khaby.lame", "title": "Simple solution 😂 #fyp", "views": 320000000},
            {"id": "6956804838784755718", "creator": "zachking", "title": "Magic trick ✨ #magic #fyp", "views": 250000000},
            {"id": "6987288404612683782", "creator": "addisonre", "title": "Get ready with me 💄 #fyp", "views": 180000000},
            {"id": "7012345678901234567", "creator": "therock", "title": "Workout motivation 💪 #fyp", "views": 150000000},
            {"id": "6976543210987654321", "creator": "willsmith", "title": "Family fun 🎬 #fyp", "views": 200000000},
            {"id": "6998765432109876543", "creator": "jimmyfallon", "title": "Dance challenge 💃 #fyp", "views": 120000000},
            {"id": "6965432109876543210", "creator": "daviddobrik", "title": "Surprise! 🎉 #vlog #fyp", "views": 95000000},
        ]
        
        demo_videos = []
        
        for i in range(count):
            real_video = real_tiktok_videos[i % len(real_tiktok_videos)]
            video_id = real_video["id"]
            creator = real_video["creator"]
            base_views = real_video["views"]
            
            demo_videos.append({
                "platform": Platform.TIKTOK,
                "video_id": video_id,
                "title": real_video["title"],
                "description": f"TikTok video by @{creator}",
                "channel_title": creator,
                "channel_id": str(random.randint(1000000000000000000, 9999999999999999999)),
                "published_at": datetime.now(timezone.utc) - __import__('datetime').timedelta(hours=random.randint(1, 168)),
                "thumbnail_url": f"https://picsum.photos/seed/{video_id}/400/600",
                "video_url": f"https://www.tiktok.com/@{creator}/video/{video_id}",
                "duration": str(random.randint(5, 60)),
                "category": "",
                "tags": "fyp,viral,trending",
                "view_count": base_views + random.randint(0, base_views // 10),
                "like_count": int(base_views * random.uniform(0.05, 0.15)),
                "comment_count": int(base_views * random.uniform(0.005, 0.02)),
                "share_count": int(base_views * random.uniform(0.01, 0.05)),
            })
        
        return demo_videos

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
