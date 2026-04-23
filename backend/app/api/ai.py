from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.analyzers.ai_analyzer import AIAnalyzer

router = APIRouter(prefix="/ai", tags=["ai"])


class TitleAnalysisRequest(BaseModel):
    platform: str
    title: str


class NicheAnalysisRequest(BaseModel):
    keyword: str
    platform: str


class TrendPredictionRequest(BaseModel):
    platform: str


class RevenueCalcRequest(BaseModel):
    platform: str
    views: int
    category: str = "general"
    region: str = "us"


@router.post("/analyze-title")
def analyze_title(request: TitleAnalysisRequest, db: Session = Depends(get_db)):
    analyzer = AIAnalyzer(db)
    result = analyzer.analyze_title(platform=request.platform, title=request.title)
    return result


@router.post("/analyze-niche")
def analyze_niche(request: NicheAnalysisRequest, db: Session = Depends(get_db)):
    analyzer = AIAnalyzer(db)
    result = analyzer.analyze_niche(keyword=request.keyword, platform=request.platform)
    return result


@router.post("/predict-trend")
def predict_trend(request: TrendPredictionRequest, db: Session = Depends(get_db)):
    analyzer = AIAnalyzer(db)
    result = analyzer.predict_trend(platform=request.platform)
    return result


@router.post("/calculate-revenue")
def calculate_revenue(request: RevenueCalcRequest, db: Session = Depends(get_db)):
    analyzer = AIAnalyzer(db)
    result = analyzer.calculate_revenue(
        platform=request.platform,
        views=request.views,
        category=request.category,
        region=request.region,
    )
    return result
