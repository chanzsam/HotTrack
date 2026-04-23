import os
from dotenv import load_dotenv

load_dotenv()


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


settings = Settings()
