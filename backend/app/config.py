import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class Settings:
    PROJECT_NAME: str = "HotTrack - YouTube & TikTok 热门视频分析平台"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./hottrack.db")

    YOUTUBE_API_KEY: str = os.getenv("YOUTUBE_API_KEY", "")
    YOUTUBE_API_ENABLED: bool = bool(os.getenv("YOUTUBE_API_KEY", ""))

    TIKHUB_API_KEY: str = os.getenv("TIKHUB_API_KEY", "")
    TIKHUB_ENABLED: bool = bool(os.getenv("TIKHUB_API_KEY", ""))

    TIKTOK_ENABLED: bool = os.getenv("TIKTOK_ENABLED", "true").lower() == "true"

    CRAWL_INTERVAL_MINUTES: int = int(os.getenv("CRAWL_INTERVAL_MINUTES", "60"))

    CORS_ORIGINS: list = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:3000",
    ]
    
    def __init__(self):
        logger.info(f"[Config] YOUTUBE_API_KEY: {'已配置' if self.YOUTUBE_API_KEY else '未配置'} (长度: {len(self.YOUTUBE_API_KEY)})")
        logger.info(f"[Config] TIKHUB_API_KEY: {'已配置' if self.TIKHUB_API_KEY else '未配置'} (长度: {len(self.TIKHUB_API_KEY)})")
        logger.info(f"[Config] YOUTUBE_API_ENABLED: {self.YOUTUBE_API_ENABLED}")
        logger.info(f"[Config] TIKHUB_ENABLED: {self.TIKHUB_ENABLED}")


settings = Settings()
