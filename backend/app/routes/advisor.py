from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.portfolio import AdvisorAdvice
from app.services.advisor_service import AdvisorService
from app.services.portfolio_service import PortfolioService
from app.services.risk_service import RiskService
from app.middleware.auth_middleware import get_current_user
from app.models.user import User

router = APIRouter(prefix="/advisor", tags=["advisor"])


@router.post("", response_model=AdvisorAdvice)
def get_advice(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI-powered portfolio advice"""
    
    # Get portfolio data
    summary = PortfolioService.get_portfolio_summary(db, current_user.id)
    features = PortfolioService.get_portfolio_features(db, current_user.id)
    risk = RiskService.predict_risk(db, current_user.id)
    
    # Generate advice
    advice = AdvisorService.get_advice(db, current_user.id, summary, features, risk)
    
    return advice
