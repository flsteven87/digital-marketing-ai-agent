from typing import Any, List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query

from app.schemas.analytics import (
    AnalyticsReport,
    MetricsSummary,
    PerformanceMetrics,
    ContentPerformance
)
from app.schemas.user import User
from app.services.analytics.analytics_service import AnalyticsService
from app.api.deps import get_current_user

router = APIRouter()
analytics_service = AnalyticsService()


@router.get("/overview", response_model=MetricsSummary)
async def get_analytics_overview(
    current_user: User = Depends(get_current_user),
    start_date: datetime = Query(default=None),
    end_date: datetime = Query(default=None),
    brand_id: str = Query(default=None)
) -> Any:
    if not start_date:
        start_date = datetime.now() - timedelta(days=30)
    if not end_date:
        end_date = datetime.now()
    
    overview = await analytics_service.get_metrics_summary(
        user_id=current_user.id,
        brand_id=brand_id,
        start_date=start_date,
        end_date=end_date
    )
    return overview


@router.get("/performance", response_model=PerformanceMetrics)
async def get_performance_metrics(
    current_user: User = Depends(get_current_user),
    metric_type: str = Query(default="engagement"),
    period: str = Query(default="week"),
    platform: str = Query(default=None)
) -> Any:
    metrics = await analytics_service.get_performance_metrics(
        user_id=current_user.id,
        metric_type=metric_type,
        period=period,
        platform=platform
    )
    return metrics


@router.get("/content-performance", response_model=List[ContentPerformance])
async def get_content_performance(
    current_user: User = Depends(get_current_user),
    content_type: str = Query(default=None),
    sort_by: str = Query(default="engagement_rate"),
    limit: int = Query(default=10)
) -> Any:
    performance = await analytics_service.get_content_performance(
        user_id=current_user.id,
        content_type=content_type,
        sort_by=sort_by,
        limit=limit
    )
    return performance


@router.get("/reports/weekly", response_model=AnalyticsReport)
async def get_weekly_report(
    current_user: User = Depends(get_current_user),
    week_offset: int = Query(default=0)
) -> Any:
    report = await analytics_service.generate_weekly_report(
        user_id=current_user.id,
        week_offset=week_offset
    )
    return report


@router.get("/reports/monthly", response_model=AnalyticsReport)
async def get_monthly_report(
    current_user: User = Depends(get_current_user),
    month: int = Query(default=None),
    year: int = Query(default=None)
) -> Any:
    if not month:
        month = datetime.now().month
    if not year:
        year = datetime.now().year
    
    report = await analytics_service.generate_monthly_report(
        user_id=current_user.id,
        month=month,
        year=year
    )
    return report


@router.get("/insights")
async def get_ai_insights(
    current_user: User = Depends(get_current_user),
    focus_area: str = Query(default="general")
) -> Any:
    insights = await analytics_service.generate_ai_insights(
        user_id=current_user.id,
        focus_area=focus_area
    )
    return insights


@router.get("/competitors")
async def get_competitor_analysis(
    current_user: User = Depends(get_current_user),
    industry: str = Query(default=None)
) -> Any:
    analysis = await analytics_service.get_competitor_analysis(
        user_id=current_user.id,
        industry=industry
    )
    return analysis


@router.post("/export")
async def export_analytics_data(
    current_user: User = Depends(get_current_user),
    format: str = Query(default="csv"),
    start_date: datetime = Query(default=None),
    end_date: datetime = Query(default=None)
) -> Any:
    export_url = await analytics_service.export_data(
        user_id=current_user.id,
        format=format,
        start_date=start_date,
        end_date=end_date
    )
    return {"export_url": export_url}