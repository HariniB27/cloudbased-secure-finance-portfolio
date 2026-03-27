from sqlalchemy.orm import Session
from typing import Dict
from datetime import datetime
from app.models.asset import Asset, AssetType
from app.schemas.portfolio import (
    AllocationBreakdown,
    PortfolioSummary,
    PortfolioFeatures,
    PerformanceMetrics,
    AssetPerformance,
)
from app.ml.feature_extractor import FeatureExtractor


class PortfolioService:
    """Service for portfolio analytics and summary"""
    
    @staticmethod
    def get_portfolio_summary(db: Session, user_id: int) -> PortfolioSummary:
        """Get portfolio summary with totals and allocation"""
        assets = db.query(Asset).filter(Asset.user_id == user_id).all()
        
        if not assets:
            return PortfolioSummary(
                total_invested=0.0,
                total_current=0.0,
                total_profit_loss=0.0,
                total_profit_loss_percentage=0.0,
                allocation_breakdown=AllocationBreakdown(),
                last_refreshed=datetime.utcnow()
            )
        
        # Calculate totals
        total_invested = sum(asset.invested_amount for asset in assets)
        total_current = sum(asset.current_value for asset in assets)
        total_pl = total_current - total_invested
        total_pl_pct = (total_pl / total_invested * 100) if total_invested > 0 else 0.0
        
        # Calculate allocation breakdown
        allocation = AllocationBreakdown()
        
        for asset in assets:
            value = asset.current_value
            
            if asset.asset_type == AssetType.EQUITY:
                allocation.equity += value
            elif asset.asset_type == AssetType.DEBT:
                allocation.debt += value
            elif asset.asset_type == AssetType.MUTUAL_FUND:
                allocation.mutual_fund += value
            elif asset.asset_type == AssetType.GOLD:
                allocation.gold += value
            elif asset.asset_type == AssetType.SILVER:
                allocation.silver += value
            elif asset.asset_type == AssetType.CASH:
                allocation.cash += value
        
        # Get most recent update time
        last_refreshed = max(
            (asset.last_updated for asset in assets),
            default=datetime.utcnow()
        )
        
        return PortfolioSummary(
            total_invested=round(total_invested, 2),
            total_current=round(total_current, 2),
            total_profit_loss=round(total_pl, 2),
            total_profit_loss_percentage=round(total_pl_pct, 2),
            allocation_breakdown=allocation,
            last_refreshed=last_refreshed
        )
    
    @staticmethod
    def get_portfolio_features(db: Session, user_id: int) -> PortfolioFeatures:
        """Get portfolio features for risk analysis"""
        assets = db.query(Asset).filter(Asset.user_id == user_id).all()
        
        features_dict = FeatureExtractor.calculate_features(assets)
        
        return PortfolioFeatures(**features_dict)
    
    @staticmethod
    def get_assets_by_type(db: Session, user_id: int) -> Dict[str, list]:
        """Group assets by type for display"""
        assets = db.query(Asset).filter(Asset.user_id == user_id).all()
        
        grouped = {
            "equity": [],
            "debt_mutual_funds": [],
            "commodities": [],
            "cash": []
        }
        
        for asset in assets:
            if asset.asset_type == AssetType.EQUITY:
                grouped["equity"].append(asset)
            elif asset.asset_type in [AssetType.DEBT, AssetType.MUTUAL_FUND]:
                grouped["debt_mutual_funds"].append(asset)
            elif asset.asset_type in [AssetType.GOLD, AssetType.SILVER]:
                grouped["commodities"].append(asset)
            elif asset.asset_type == AssetType.CASH:
                grouped["cash"].append(asset)
        
        return grouped

    @staticmethod
    def get_performance_metrics(db: Session, user_id: int) -> PerformanceMetrics:
        assets = db.query(Asset).filter(Asset.user_id == user_id).all()
        if not assets:
            return PerformanceMetrics(
                absolute_return_percentage=0.0,
                annualized_return_percentage=0.0,
                best_performing_asset=None,
                worst_performing_asset=None,
            )

        total_invested = sum(a.invested_amount for a in assets)
        total_current = sum(a.current_value for a in assets)
        absolute_return_pct = ((total_current - total_invested) / total_invested * 100) if total_invested else 0.0

        annualized_candidates = []
        now = datetime.utcnow()
        for asset in assets:
            if asset.invested_amount <= 0:
                continue
            purchase_date = asset.purchase_date or now
            holding_days = max((now - purchase_date).days, 1)
            years = holding_days / 365.25
            total_return = (asset.current_value / asset.invested_amount) - 1
            try:
                annualized = ((1 + total_return) ** (1 / years) - 1) * 100 if years > 0 and (1 + total_return) > 0 else -100.0
            except Exception:
                annualized = 0.0
            annualized_candidates.append((asset.current_value, annualized))
        annualized_return_pct = 0.0
        if annualized_candidates:
            total_weight = sum(weight for weight, _ in annualized_candidates)
            if total_weight > 0:
                annualized_return_pct = sum(weight * val for weight, val in annualized_candidates) / total_weight

        def to_asset_perf(asset: Asset) -> AssetPerformance:
            gain_loss = asset.current_value - asset.invested_amount
            return_pct = (gain_loss / asset.invested_amount * 100) if asset.invested_amount else 0.0
            return AssetPerformance(
                asset_id=asset.id,
                name=asset.name,
                asset_type=asset.asset_type.value,
                return_percentage=round(return_pct, 2),
                gain_loss=round(gain_loss, 2),
            )

        sorted_assets = sorted(
            assets,
            key=lambda a: ((a.current_value - a.invested_amount) / a.invested_amount) if a.invested_amount else -9999
        )
        worst = to_asset_perf(sorted_assets[0]) if sorted_assets else None
        best = to_asset_perf(sorted_assets[-1]) if sorted_assets else None

        return PerformanceMetrics(
            absolute_return_percentage=round(absolute_return_pct, 2),
            annualized_return_percentage=round(annualized_return_pct, 2),
            best_performing_asset=best,
            worst_performing_asset=worst,
        )
