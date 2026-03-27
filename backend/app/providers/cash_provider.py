from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import Dict


class CashProvider:
    """Provider for Fixed Deposit / Cash asset calculations"""
    
    @staticmethod
    def calculate_maturity_date(purchase_date: datetime, term_months: int) -> datetime:
        """
        Calculate FD maturity date
        
        Args:
            purchase_date: When FD was started
            term_months: Term in months (e.g., 12 for 1 year)
            
        Returns:
            Maturity date
        """
        return purchase_date + relativedelta(months=term_months)
    
    @staticmethod
    def calculate_current_value(
        deposit_amount: float,
        interest_rate: float,
        purchase_date: datetime,
        interest_type: str = 'compound'
    ) -> float:
        """
        Calculate current FD value with accrued interest
        
        Args:
            deposit_amount: Principal amount deposited
            interest_rate: Annual interest rate (e.g., 6.5 for 6.5%)
            purchase_date: When FD was started
            interest_type: 'simple' or 'compound'
        
        Returns:
            Current value with accrued interest
        """
        # Calculate time elapsed
        today = datetime.utcnow()
        days_elapsed = (today - purchase_date).days
        
        # Handle edge case: same day
        if days_elapsed <= 0:
            return deposit_amount
        
        # Convert to years
        years_elapsed = days_elapsed / 365.0
        
        # Calculate based on interest type
        annual_rate = interest_rate / 100.0
        
        if interest_type == 'simple':
            # Simple Interest: P + (P × R × T)
            interest = deposit_amount * annual_rate * years_elapsed
            current_value = deposit_amount + interest
        else:
            # Compound Interest: P × (1 + R)^T
            current_value = deposit_amount * ((1 + annual_rate) ** years_elapsed)
        
        return round(current_value, 2)
    
    @staticmethod
    def get_fd_details(
        deposit_amount: float,
        interest_rate: float,
        term_months: int,
        purchase_date: datetime,
        interest_type: str = 'compound'
    ) -> Dict:
        """
        Get complete FD details including maturity info
        
        Args:
            deposit_amount: Principal amount
            interest_rate: Annual rate (%)
            term_months: Term in months
            purchase_date: Start date
            interest_type: 'simple' or 'compound'
            
        Returns:
            Dictionary with current_value, maturity_value, maturity_date, etc.
        """
        maturity_date = CashProvider.calculate_maturity_date(purchase_date, term_months)
        current_value = CashProvider.calculate_current_value(
            deposit_amount, interest_rate, purchase_date, interest_type
        )
        
        # Calculate maturity value (what you'll get at the end)
        years = term_months / 12.0
        annual_rate = interest_rate / 100.0
        
        if interest_type == 'simple':
            maturity_value = deposit_amount * (1 + annual_rate * years)
        else:
            maturity_value = deposit_amount * ((1 + annual_rate) ** years)
        
        # Check if matured
        is_matured = datetime.utcnow() >= maturity_date
        
        return {
            "current_value": round(current_value, 2),
            "maturity_value": round(maturity_value, 2),
            "maturity_date": maturity_date,
            "is_matured": is_matured,
            "days_to_maturity": (maturity_date - datetime.utcnow()).days if not is_matured else 0
        }
