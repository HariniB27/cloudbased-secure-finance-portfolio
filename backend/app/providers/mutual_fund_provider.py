import requests
from typing import Optional, Dict
from datetime import datetime
import time


class MutualFundProvider:
    """
    Provider for Indian Mutual Fund NAV data
    Uses mfapi.in (free India MF NAV API)
    """
    
    BASE_URL = "https://api.mfapi.in/mf"
    
    @staticmethod
    def get_nav(scheme_code: str) -> Optional[Dict]:
        """
        Get latest NAV for a mutual fund scheme
        
        Args:
            scheme_code: AMFI scheme code (e.g., "119551" for Axis Bluechip)
        
        Returns:
            Dict with nav, scheme_name, last_updated, source
        """
        try:
            url = f"{MutualFundProvider.BASE_URL}/{scheme_code}"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            if not data or "data" not in data:
                return None
            
            latest_data = data["data"][0] if data["data"] else None
            
            if not latest_data:
                return None
            
            nav = float(latest_data.get("nav", 0))
            date_str = latest_data.get("date", "")
            
            if nav == 0:
                return None
            
            return {
                "nav": nav,
                "scheme_name": data.get("meta", {}).get("scheme_name", "Unknown"),
                "scheme_code": scheme_code,
                "last_updated": datetime.utcnow(),
                "nav_date": date_str,
                "source": "mfapi.in"
            }
        
        except requests.exceptions.RequestException as e:
            print(f"Network error fetching NAV for {scheme_code}: {str(e)}")
            return None
        except Exception as e:
            print(f"Error fetching NAV for {scheme_code}: {str(e)}")
            return None
    
    @staticmethod
    def search_scheme(scheme_name: str) -> list:
        """
        Search for mutual fund schemes by name
        
        Args:
            scheme_name: Partial or full scheme name
        
        Returns:
            List of matching schemes with codes
        """
        try:
            # Note: mfapi.in doesn't have search, so this is a placeholder
            # In production, you might cache the full scheme list
            return []
        except Exception as e:
            print(f"Error searching schemes: {str(e)}")
            return []
    
    @staticmethod
    def get_batch_nav(scheme_codes: list) -> Dict[str, Optional[Dict]]:
        """
        Get NAV for multiple schemes
        
        Args:
            scheme_codes: List of scheme codes
        
        Returns:
            Dict mapping scheme_code to NAV data
        """
        results = {}
        
        for code in scheme_codes:
            results[code] = MutualFundProvider.get_nav(code)
            # Small delay to avoid rate limiting
            time.sleep(0.2)
        
        return results
    
    @staticmethod
    def validate_scheme_code(scheme_code: str) -> bool:
        """Check if a scheme code is valid"""
        result = MutualFundProvider.get_nav(scheme_code)
        return result is not None
