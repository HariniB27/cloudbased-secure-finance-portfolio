from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.pdf_service import PDFService
from app.services.asset_service import AssetService
from app.services.portfolio_service import PortfolioService
from app.services.risk_service import RiskService
from app.services.advisor_service import AdvisorService
from app.middleware.auth_middleware import get_current_user
from app.models.user import User

router = APIRouter(prefix="/export", tags=["export"])


@router.get("/pdf")
def export_pdf(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export portfolio report as PDF"""
    
    # Gather all data
    assets = AssetService.get_assets(db, current_user.id)
    summary = PortfolioService.get_portfolio_summary(db, current_user.id)
    features = PortfolioService.get_portfolio_features(db, current_user.id)
    risk = RiskService.predict_risk(db, current_user.id)
    advice = AdvisorService.get_advice(db, current_user.id, summary, features, risk)
    
    # Generate PDF
    pdf_buffer = PDFService.generate_portfolio_report(
        assets=assets,
        summary=summary,
        risk=risk,
        advice=advice,
        username=current_user.username
    )
    
    # Return as downloadable file
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=portfolio_report_{current_user.username}.pdf"
        }
    )
