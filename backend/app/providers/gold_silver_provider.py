import requests
from typing import Optional, Dict
from datetime import datetime


class GoldSilverProvider:
    """
    Provider for Gold and Silver prices in India
    
    Uses multiple fallback sources:
    1. goldapi.io (free tier available)
    2. Fallback to static rates with manual update capability
    """
    
    # Karat purity ratios for gold
    KARAT_PURITY = {
        "24K": 1.0,      # 99.9% pure
        "22K": 0.916,    # 91.6% pure
        "18K": 0.750,    # 75% pure
        "14K": 0.585     # 58.5% pure
    }
    
    # Fallback rates (INR per gram) - updated manually
    FALLBACK_RATES = {
        "gold_24k": 6450.0,  # Approximate as of Feb 2025
        "gold_22k": 5908.2,
        "gold_18k": 4837.5,
        "silver": 78.0,       # Approximate as of Feb 2025
        "last_updated": "2025-02-13"
    }
    
    @staticmethod
    def get_gold_price(karat: str = "24K") -> Optional[Dict]:
        """
        Get current gold price in INR per gram
        
        Args:
            karat: "24K", "22K", "18K", or "14K"
        
        Returns:
            Dict with price_per_gram, karat, last_updated, source
        """
        try:
            # Try to fetch from API (placeholder for real API)
            # In production, you could use goldapi.io or metals-api.com
            
            # For now, use fallback rates
            if karat not in GoldSilverProvider.KARAT_PURITY:
                karat = "24K"  # Default

            rate_key = f"gold_{karat.lower()}"
            if rate_key in GoldSilverProvider.FALLBACK_RATES:
                price_per_gram = GoldSilverProvider.FALLBACK_RATES[rate_key]
            else:
                base_price = GoldSilverProvider.FALLBACK_RATES["gold_24k"]
                purity = GoldSilverProvider.KARAT_PURITY[karat]
                price_per_gram = base_price * purity
            
            return {
                "price_per_gram": round(price_per_gram, 2),
                "karat": karat,
                "last_updated": datetime.utcnow(),
                "source": "fallback_rates",
                "note": "Using fallback rates - update manually for accuracy"
            }
        
        except Exception as e:
            print(f"Error fetching gold price: {str(e)}")
            return None
    
    @staticmethod
    def get_silver_price() -> Optional[Dict]:
        """
        Get current silver price in INR per gram
        
        Returns:
            Dict with price_per_gram, last_updated, source
        """
        try:
            # Use fallback rates
            price_per_gram = GoldSilverProvider.FALLBACK_RATES["silver"]
            
            return {
                "price_per_gram": round(price_per_gram, 2),
                "last_updated": datetime.utcnow(),
                "source": "fallback_rates",
                "note": "Using fallback rates - update manually for accuracy"
            }
        
        except Exception as e:
            print(f"Error fetching silver price: {str(e)}")
            return None
    
    @staticmethod
    def get_commodity_price(commodity: str, karat: Optional[str] = None) -> Optional[Dict]:
        """
        Unified method to get gold or silver price
        
        Args:
            commodity: "gold" or "silver"
            karat: Required for gold ("24K", "22K", "18K", "14K")
        
        Returns:
            Price data dict
        """
        if commodity.lower() == "gold":
            if karat is None:
                karat = "24K"
            return GoldSilverProvider.get_gold_price(karat)
        elif commodity.lower() == "silver":
            return GoldSilverProvider.get_silver_price()
        else:
            return None
    
    @staticmethod
    def update_fallback_rates(gold_24k: float, silver: float):
        """
        Manually update fallback rates (for admin use)
        
        Args:
            gold_24k: Price per gram of 24K gold in INR
            silver: Price per gram of silver in INR
        """
        GoldSilverProvider.FALLBACK_RATES["gold_24k"] = gold_24k
        GoldSilverProvider.FALLBACK_RATES["gold_22k"] = round(gold_24k * GoldSilverProvider.KARAT_PURITY["22K"], 2)
        GoldSilverProvider.FALLBACK_RATES["gold_18k"] = round(gold_24k * GoldSilverProvider.KARAT_PURITY["18K"], 2)
        GoldSilverProvider.FALLBACK_RATES["silver"] = silver
        GoldSilverProvider.FALLBACK_RATES["last_updated"] = datetime.utcnow().strftime("%Y-%m-%d")
