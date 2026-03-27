import numpy as np
from typing import Dict, List
from app.models.asset import Asset, AssetType


class FeatureExtractor:
    """Extract market-style features from portfolio for risk classification"""
    
    # Risk weights for volatility calculation
    ASSET_RISK_WEIGHTS = {
        AssetType.EQUITY: 0.30,          # High volatility
        AssetType.MUTUAL_FUND: 0.15,     # Medium-high volatility
        AssetType.DEBT: 0.05,            # Low volatility
        AssetType.GOLD: 0.12,            # Medium volatility
        AssetType.SILVER: 0.18,          # Medium-high volatility
        AssetType.CASH: 0.01             # Very low volatility
    }
    
    @staticmethod
    def calculate_features(assets: List[Asset]) -> Dict[str, float]:
        """
        Calculate deterministic portfolio features for risk model
        
        Features:
        - total_return: (current - invested) / invested
        - volatility_proxy: Weighted risk score based on allocation
        - momentum_proxy: 0 (no price history), could be enhanced
        - drawdown_proxy: Based on concentration risk
        - risk_score: return / (volatility + epsilon)
        - equity_allocation: % in equity
        - debt_allocation: % in debt + mutual funds
        - commodity_allocation: % in gold + silver
        - cash_allocation: % in cash
        - concentration_hhi: Herfindahl-Hirschman Index
        """
        if not assets:
            return {
                "total_return": 0.0,
                "volatility_proxy": 0.0,
                "momentum_proxy": 0.0,
                "drawdown_proxy": 0.0,
                "risk_score": 0.0,
                "equity_allocation": 0.0,
                "debt_allocation": 0.0,
                "commodity_allocation": 0.0,
                "cash_allocation": 0.0,
                "concentration_hhi": 0.0
            }
        
        # Calculate totals
        total_invested = sum(asset.invested_amount for asset in assets)
        total_current = sum(asset.current_value for asset in assets)
        
        if total_invested == 0:
            total_invested = 1.0  # Avoid division by zero
        
        # Total return
        total_return = (total_current - total_invested) / total_invested
        
        # Calculate allocations by asset type
        allocations = {
            AssetType.EQUITY: 0.0,
            AssetType.MUTUAL_FUND: 0.0,
            AssetType.DEBT: 0.0,
            AssetType.GOLD: 0.0,
            AssetType.SILVER: 0.0,
            AssetType.CASH: 0.0
        }
        
        asset_weights = []  # For HHI calculation
        
        for asset in assets:
            allocation = asset.current_value / total_current if total_current > 0 else 0
            allocations[asset.asset_type] += allocation
            asset_weights.append(allocation)
        
        # Grouped allocations
        equity_allocation = allocations[AssetType.EQUITY]
        debt_allocation = allocations[AssetType.DEBT] + allocations[AssetType.MUTUAL_FUND]
        commodity_allocation = allocations[AssetType.GOLD] + allocations[AssetType.SILVER]
        cash_allocation = allocations[AssetType.CASH]
        
        # Volatility proxy (weighted by asset type risk)
        volatility_proxy = 0.0
        for asset_type, allocation in allocations.items():
            risk_weight = FeatureExtractor.ASSET_RISK_WEIGHTS.get(asset_type, 0.1)
            volatility_proxy += allocation * risk_weight
        
        # Momentum proxy (no price history, so using 0)
        # In a real system, this would be calculated from historical prices
        momentum_proxy = 0.0
        
        # Drawdown proxy based on concentration (HHI)
        # Higher concentration = higher potential drawdown
        concentration_hhi = sum(w**2 for w in asset_weights)
        drawdown_proxy = concentration_hhi * volatility_proxy
        
        # Risk score (Sharpe-like ratio)
        epsilon = 1e-6
        risk_score = total_return / (volatility_proxy + epsilon)
        
        return {
            "total_return": round(total_return, 4),
            "volatility_proxy": round(volatility_proxy, 4),
            "momentum_proxy": round(momentum_proxy, 4),
            "drawdown_proxy": round(drawdown_proxy, 4),
            "risk_score": round(risk_score, 4),
            "equity_allocation": round(equity_allocation, 4),
            "debt_allocation": round(debt_allocation, 4),
            "commodity_allocation": round(commodity_allocation, 4),
            "cash_allocation": round(cash_allocation, 4),
            "concentration_hhi": round(concentration_hhi, 4)
        }
    
    @staticmethod
    def get_feature_vector(assets: List[Asset]) -> np.ndarray:
        """Get feature vector as numpy array for ML model"""
        features = FeatureExtractor.calculate_features(assets)
        
        # Feature order must match training data
        feature_vector = np.array([
            features["total_return"],
            features["volatility_proxy"],
            features["momentum_proxy"],
            features["drawdown_proxy"],
            features["risk_score"],
            features["equity_allocation"],
            features["debt_allocation"],
            features["commodity_allocation"],
            features["cash_allocation"],
            features["concentration_hhi"]
        ]).reshape(1, -1)
        
        return feature_vector
