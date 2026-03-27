from pydantic import BaseModel
from typing import Dict, List
from datetime import datetime


class AllocationBreakdown(BaseModel):
    equity: float = 0.0
    debt: float = 0.0
    mutual_fund: float = 0.0
    gold: float = 0.0
    silver: float = 0.0
    cash: float = 0.0


class PortfolioSummary(BaseModel):
    total_invested: float
    total_current: float
    total_profit_loss: float
    total_profit_loss_percentage: float
    allocation_breakdown: AllocationBreakdown
    last_refreshed: datetime


class PortfolioFeatures(BaseModel):
    total_return: float  # (current - invested) / invested
    volatility_proxy: float  # Weighted risk score based on allocation
    momentum_proxy: float  # Rolling price change proxy
    drawdown_proxy: float  # Max drawdown proxy
    risk_score: float  # return / (volatility + epsilon)
    equity_allocation: float
    debt_allocation: float
    commodity_allocation: float
    cash_allocation: float
    concentration_hhi: float  # Herfindahl-Hirschman Index


class RiskPrediction(BaseModel):
    risk_label: str  # "LOW", "MODERATE", "HIGH"
    confidence: float
    features_used: Dict[str, float]


class AdvisorAdvice(BaseModel):
    portfolio_health: str
    risk_reduction_actions: List[str]
    diversification_insights: List[str]
    scenario_insights: str
    strategy_recommendation: str
    provider: str = "mock"
    model: str = "rules"
    generated_at: datetime


class AssetPerformance(BaseModel):
    asset_id: int
    name: str
    asset_type: str
    return_percentage: float
    gain_loss: float


class PerformanceMetrics(BaseModel):
    absolute_return_percentage: float
    annualized_return_percentage: float
    best_performing_asset: AssetPerformance | None
    worst_performing_asset: AssetPerformance | None
