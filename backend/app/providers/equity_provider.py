from typing import Optional, Dict
from app.providers.nse_provider import NSEProvider

class EquityProvider:
    """Provider for equity (stock) data using NSE/BSE India API"""

    @staticmethod
    def get_current_price(symbol: str, exchange: str = "NSE") -> Optional[Dict[str, float]]:
        """
        Get current stock price
        
        Args:
            symbol: Stock symbol (e.g., 'RELIANCE', 'TCS')
            exchange: Exchange - 'NSE' or 'BSE'
        
        Returns:
            Dict with price and source, or None
        """
        try:
            nse = NSEProvider()
            normalized_symbol = symbol.replace(".NS", "").replace(".BO", "").replace(".BSE", "").upper()
            print(f"Fetching {normalized_symbol} from {exchange}")

            price = nse.get_stock_price(normalized_symbol, exchange)
            if price is not None:
                return {"price": float(price), "source": "nse_or_fallback"}

            print(f"❌ Could not fetch price for {normalized_symbol} on {exchange}")
            return None
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            return None
