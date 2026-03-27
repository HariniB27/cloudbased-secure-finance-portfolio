from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.portfolio import RiskPrediction
from app.services.risk_service import RiskService
from app.middleware.auth_middleware import get_current_user
from app.models.user import User

router = APIRouter(prefix="/risk", tags=["risk"])


@router.post("/predict", response_model=RiskPrediction)
def predict_risk(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Predict portfolio risk level using ML model"""
    prediction = RiskService.predict_risk(db, current_user.id)
    return prediction
