from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
import enum


class AssetType(str, enum.Enum):
    EQUITY = "equity"
    DEBT = "debt"
    MUTUAL_FUND = "mutual_fund"
    GOLD = "gold"
    SILVER = "silver"
    CASH = "cash"


class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Asset identification
    asset_type = Column(SQLEnum(AssetType), nullable=False)
    name = Column(String, nullable=False)  # Stock symbol, MF name, "Gold 24K", "SBI FD", etc.
    symbol = Column(String, nullable=True)  # For equity: RELIANCE, For MF: scheme code
    
    # Financial data
    invested_amount = Column(Float, nullable=False)  # Total amount invested (for FD: principal)
    current_value = Column(Float, nullable=False)  # Current market value (for FD: principal + interest)
    quantity = Column(Float, nullable=True)  # Shares, units, grams, etc.
    
    # Equity specific
    exchange = Column(String, nullable=True)  # NSE or BSE
    
    # Gold/Silver specific
    karat = Column(String, nullable=True)  # "24K", "22K", "18K", "14K" for gold
    
    # FD/Cash specific fields
    interest_rate = Column(Float, nullable=True)  # Annual interest rate (%)
    term_months = Column(Integer, nullable=True)  # FD term in months (e.g., 12, 24, 36)
    interest_type = Column(String, nullable=True, default='compound')  # 'simple' or 'compound'
    maturity_date = Column(DateTime, nullable=True)  # Auto-calculated: purchase_date + term_months
    
    # Metadata
    purchase_date = Column(DateTime, default=datetime.utcnow)  # When asset was bought / FD started
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notes = Column(String, nullable=True)
    
    # Relationships
    owner = relationship("User", back_populates="assets")