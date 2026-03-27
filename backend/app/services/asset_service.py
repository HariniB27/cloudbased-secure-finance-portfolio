from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
from app.models.asset import Asset, AssetType
from app.schemas.asset import AssetCreate, AssetUpdate
from app.providers import EquityProvider, GoldSilverProvider, MutualFundProvider
from fastapi import HTTPException


class AssetService:
    """Service for managing assets and updating prices"""

    @staticmethod
    def _to_utc_naive(dt: datetime) -> datetime:
        """
        Normalize datetimes for DB + comparisons.
        - If timezone-aware: convert to UTC and drop tzinfo
        - If naive: treat as UTC naive
        """
        if dt.tzinfo is not None:
            return dt.astimezone(timezone.utc).replace(tzinfo=None)
        return dt
    
    @staticmethod
    def create_asset(db: Session, user_id: int, asset_data: AssetCreate) -> Asset:
        """Create a new asset"""
        # Validate purchase_date for all asset types
        if not asset_data.purchase_date:
            raise HTTPException(400, "Investment date is required")
        purchase_date = AssetService._to_utc_naive(asset_data.purchase_date)
        if purchase_date > datetime.now(timezone.utc).replace(tzinfo=None):
            raise HTTPException(400, "Investment date cannot be in the future")

        # Initialize current_value same as invested_amount
        current_value = asset_data.invested_amount
        maturity_date = None
        
        # Handle Cash/FD assets specially
        if asset_data.asset_type == AssetType.CASH:
            # Validate required FD fields
            if not asset_data.interest_rate:
                raise HTTPException(400, "Interest rate required for FD/Cash")
            if not asset_data.term_months:
                raise HTTPException(400, "Term (months) required for FD/Cash")
            
            # Use invested_amount as principal
            principal = asset_data.invested_amount
            purchase_date = purchase_date
            
            # Calculate maturity date
            maturity_date = purchase_date + relativedelta(months=asset_data.term_months)
            
            # Calculate initial current value (same as principal on day 1)
            current_value = principal
        
        else:
            # Try to get real-time price for other asset types
            price_data = AssetService._fetch_current_price(asset_data)
            if price_data and asset_data.quantity:
                current_value = price_data * asset_data.quantity
        
        db_asset = Asset(
            user_id=user_id,
            asset_type=asset_data.asset_type,
            name=asset_data.name,
            symbol=asset_data.symbol,
            invested_amount=asset_data.invested_amount,
            current_value=current_value,
            quantity=asset_data.quantity,
            exchange=asset_data.exchange,
            karat=asset_data.karat,
            
            # FD/Cash specific fields
            interest_rate=asset_data.interest_rate,
            term_months=asset_data.term_months,
            interest_type=asset_data.interest_type or 'compound',
            maturity_date=maturity_date,
            purchase_date=purchase_date,
        )
        
        db.add(db_asset)
        db.commit()
        db.refresh(db_asset)
        return db_asset
    
    @staticmethod
    def get_assets(db: Session, user_id: int) -> List[Asset]:
        """Get all assets for a user"""
        return db.query(Asset).filter(Asset.user_id == user_id).all()
    
    @staticmethod
    def get_asset(db: Session, asset_id: int, user_id: int) -> Optional[Asset]:
        """Get a specific asset"""
        return db.query(Asset).filter(
            Asset.id == asset_id,
            Asset.user_id == user_id
        ).first()
    
    @staticmethod
    def update_asset(db: Session, asset_id: int, user_id: int, asset_data: AssetUpdate) -> Optional[Asset]:
        """Update an asset"""
        asset = AssetService.get_asset(db, asset_id, user_id)
        if not asset:
            return None
        
        update_data = asset_data.model_dump(exclude_unset=True)

        # Validate purchase_date if provided
        if "purchase_date" in update_data and update_data["purchase_date"] is not None:
            update_data["purchase_date"] = AssetService._to_utc_naive(update_data["purchase_date"])
            if update_data["purchase_date"] > datetime.now(timezone.utc).replace(tzinfo=None):
                raise HTTPException(400, "Investment date cannot be in the future")

        for field, value in update_data.items():
            setattr(asset, field, value)
        
        # If FD fields updated, recalculate maturity date
        if asset.asset_type == AssetType.CASH and asset.term_months and asset.purchase_date:
            asset.maturity_date = asset.purchase_date + relativedelta(months=asset.term_months)
        
        db.commit()
        db.refresh(asset)
        return asset
    
    @staticmethod
    def delete_asset(db: Session, asset_id: int, user_id: int) -> bool:
        """Delete an asset"""
        asset = AssetService.get_asset(db, asset_id, user_id)
        if not asset:
            return False
        
        db.delete(asset)
        db.commit()
        return True
    
    @staticmethod
    def _fetch_current_price(asset_data: AssetCreate) -> Optional[float]:
        """Fetch current price for an asset"""
        try:
            if asset_data.asset_type == AssetType.EQUITY:
                if not asset_data.symbol:
                    return None
                price_data = EquityProvider.get_current_price(
                    asset_data.symbol,
                    asset_data.exchange or "NSE"
                )
                return price_data["price"] if price_data else None
            
            elif asset_data.asset_type == AssetType.GOLD:
                karat = asset_data.karat or "24K"
                price_data = GoldSilverProvider.get_gold_price(karat)
                return price_data["price_per_gram"] if price_data else None
            
            elif asset_data.asset_type == AssetType.SILVER:
                price_data = GoldSilverProvider.get_silver_price()
                return price_data["price_per_gram"] if price_data else None
            
            elif asset_data.asset_type in [AssetType.MUTUAL_FUND, AssetType.DEBT]:
                if not asset_data.symbol:
                    return None
                nav_data = MutualFundProvider.get_nav(asset_data.symbol)
                return nav_data["nav"] if nav_data else None
            
            return None
        except Exception as e:
            print(f"Error fetching price: {str(e)}")
            return None
    
    @staticmethod
    def refresh_asset_prices(db: Session, user_id: int) -> dict:
        """Refresh current values for all assets"""
        assets = AssetService.get_assets(db, user_id)
        updated_count = 0
        failed_assets = []
        
        for asset in assets:
            try:
                new_value = AssetService._calculate_current_value(asset)
                if new_value is not None:
                    asset.current_value = new_value
                    asset.last_updated = datetime.utcnow()
                    updated_count += 1
                else:
                    failed_assets.append(asset.name)
            except Exception as e:
                print(f"Error updating {asset.name}: {str(e)}")
                failed_assets.append(asset.name)
        
        db.commit()
        
        return {
            "total_assets": len(assets),
            "updated_count": updated_count,
            "failed_assets": failed_assets,
            "last_refreshed": datetime.utcnow()
        }
    
    @staticmethod
    def _calculate_current_value(asset: Asset) -> Optional[float]:
        """Calculate current value for an asset"""
        
        # EQUITY
        if asset.asset_type == AssetType.EQUITY:
            if not asset.symbol or not asset.quantity:
                return None
            price_data = EquityProvider.get_current_price(asset.symbol, asset.exchange or "NSE")
            if price_data:
                return price_data["price"] * asset.quantity
        
        # GOLD
        elif asset.asset_type == AssetType.GOLD:
            if not asset.quantity:
                return None
            karat = asset.karat or "24K"
            price_data = GoldSilverProvider.get_gold_price(karat)
            if price_data:
                return price_data["price_per_gram"] * asset.quantity
        
        # SILVER
        elif asset.asset_type == AssetType.SILVER:
            if not asset.quantity:
                return None
            price_data = GoldSilverProvider.get_silver_price()
            if price_data:
                return price_data["price_per_gram"] * asset.quantity
        
        # MUTUAL FUND / DEBT
        elif asset.asset_type in [AssetType.MUTUAL_FUND, AssetType.DEBT]:
            if not asset.symbol or not asset.quantity:
                return None
            nav_data = MutualFundProvider.get_nav(asset.symbol)
            if nav_data:
                return nav_data["nav"] * asset.quantity
        
        # CASH / FD
        elif asset.asset_type == AssetType.CASH:
            return AssetService._calculate_fd_value(asset)
        
        return None
    
    @staticmethod
    def _calculate_fd_value(asset: Asset) -> Optional[float]:
        """
        Calculate current FD value with accrued interest
        Supports both simple and compound interest
        """
        # Use invested_amount as principal (clean and simple!)
        principal = asset.invested_amount
        
        if not principal:
            return asset.invested_amount
        
        # If no interest rate, return principal
        if not asset.interest_rate or asset.interest_rate <= 0:
            return principal
        
        # Calculate time elapsed
        purchase_date = asset.purchase_date
        if not purchase_date:
            return principal
        
        today = datetime.utcnow()
        days_elapsed = (today - purchase_date).days
        
        # Edge case: same day or negative days
        if days_elapsed <= 0:
            return principal
        
        # Convert to years
        years_elapsed = days_elapsed / 365.0
        
        # Get interest rate as decimal
        annual_rate = asset.interest_rate / 100.0
        
        # Get interest type (default to compound)
        interest_type = asset.interest_type or 'compound'
        
        # Calculate based on interest type
        if interest_type.lower() == 'simple':
            # Simple Interest: P + (P × R × T)
            interest = principal * annual_rate * years_elapsed
            current_value = principal + interest
        else:
            # Compound Interest: P × (1 + R)^T
            current_value = principal * ((1 + annual_rate) ** years_elapsed)
        
        # Round to 2 decimal places
        return round(current_value, 2)