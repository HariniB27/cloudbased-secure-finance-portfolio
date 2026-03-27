from app.schemas.user import UserCreate, UserLogin, UserResponse, Token, TokenData
from app.schemas.asset import AssetCreate, AssetUpdate, AssetResponse
from app.schemas.portfolio import (
AllocationBreakdown,
PortfolioSummary,
PortfolioFeatures,
RiskPrediction,
AdvisorAdvice
)
all = [
"UserCreate", "UserLogin", "UserResponse", "Token", "TokenData",
"AssetCreate", "AssetUpdate", "AssetResponse",
"AllocationBreakdown", "PortfolioSummary", "PortfolioFeatures",
"RiskPrediction", "AdvisorAdvice"
]
