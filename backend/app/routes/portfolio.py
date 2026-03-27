from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.portfolio import PortfolioSummary, PortfolioFeatures, PerformanceMetrics
from app.services.portfolio_service import PortfolioService
from app.services.asset_service import AssetService
from app.middleware.auth_middleware import get_current_user
from app.models.user import User

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.post("/refresh")
def refresh_prices(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Refresh all asset prices"""
    result = AssetService.refresh_asset_prices(db, current_user.id)
    return result


@router.get("/summary", response_model=PortfolioSummary)
def get_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get portfolio summary"""
    summary = PortfolioService.get_portfolio_summary(db, current_user.id)
    return summary


@router.get("/features", response_model=PortfolioFeatures)
def get_features(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get portfolio features for risk analysis"""
    features = PortfolioService.get_portfolio_features(db, current_user.id)
    return features


@router.get("/performance", response_model=PerformanceMetrics)
def get_performance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get portfolio performance metrics."""
    return PortfolioService.get_performance_metrics(db, current_user.id)
