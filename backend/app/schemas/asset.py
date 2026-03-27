from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.asset import AssetType


class AssetCreate(BaseModel):
    asset_type: AssetType
    name: str = Field(..., min_length=1)
    symbol: Optional[str] = None
    invested_amount: float = Field(..., gt=0)
    quantity: Optional[float] = Field(None, gt=0)
    exchange: Optional[str] = None  # "NSE" or "BSE"
    karat: Optional[str] = None  # "24K", "22K", "18K", "14K"
    
    # FD/Cash specific fields - ADD THESE ↓
    interest_rate: Optional[float] = Field(None, ge=0, le=100)  # 0-100%
    term_months: Optional[int] = Field(None, gt=0)  # Term in months
    interest_type: Optional[str] = Field(default='compound')  # 'simple' or 'compound'
    
    # Actual investment/purchase date (required for all asset types)
    purchase_date: datetime
    maturity_date: Optional[datetime] = None


class AssetUpdate(BaseModel):
    name: Optional[str] = None
    symbol: Optional[str] = None
    exchange: Optional[str] = None
    karat: Optional[str] = None
    invested_amount: Optional[float] = Field(None, gt=0)
    quantity: Optional[float] = Field(None, gt=0)
    
    # FD/Cash fields - ADD THESE ↓
    interest_rate: Optional[float] = Field(None, ge=0, le=100)
    term_months: Optional[int] = Field(None, gt=0)
    interest_type: Optional[str] = None
    
    purchase_date: Optional[datetime] = None
    maturity_date: Optional[datetime] = None


class AssetResponse(BaseModel):
    id: int
    asset_type: AssetType
    name: str
    symbol: Optional[str]
    invested_amount: float
    current_value: float
    quantity: Optional[float]
    exchange: Optional[str]
    karat: Optional[str]
    
    # FD/Cash fields - ADD THESE ↓
    interest_rate: Optional[float]
    term_months: Optional[int]
    interest_type: Optional[str]
    
    maturity_date: Optional[datetime]
    purchase_date: datetime
    last_updated: datetime
    
    # Computed fields
    @property
    def profit_loss(self) -> float:
        return self.current_value - self.invested_amount
    
    @property
    def profit_loss_percentage(self) -> float:
        if self.invested_amount == 0:
            return 0.0
        return ((self.current_value - self.invested_amount) / self.invested_amount) * 100

    class Config:
        from_attributes = True