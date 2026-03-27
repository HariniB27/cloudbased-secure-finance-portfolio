import requests
from typing import Optional
import time
import yfinance as yf

class NSEProvider:
    """Fetch real-time Indian stock prices from NSE and BSE"""
    
    NSE_BASE_URL = "https://www.nseindia.com"
    BSE_BASE_URL = "https://api.bseindia.com"
    
    def __init__(self):
        # NSE session
        self.nse_session = requests.Session()
        self.nse_session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
        })
        # Get NSE cookies
        try:
            self.nse_session.get(self.NSE_BASE_URL, timeout=5)
            time.sleep(0.5)
        except:
            pass
        
        # BSE session
        self.bse_session = requests.Session()
        self.bse_session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
        })
    
    def get_nse_price(self, symbol: str) -> Optional[float]:
        """Get price from NSE"""
        try:
            clean_symbol = symbol.replace('.NS', '').replace('.BSE', '')
            url = f"{self.NSE_BASE_URL}/api/quote-equity?symbol={clean_symbol}"
            
            response = self.nse_session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                price = data.get('priceInfo', {}).get('lastPrice')
                
                if price:
                    print(f"✅ NSE price for {clean_symbol}: ₹{price}")
                    return float(price)
            
            return None
            
        except Exception as e:
            print(f"NSE API error for {symbol}: {e}")
            return None

    def get_yfinance_nse_price(self, symbol: str) -> Optional[float]:
        """Fallback for NSE symbols through yfinance (.NS)."""
        try:
            clean_symbol = symbol.replace('.NS', '').replace('.BSE', '').replace('.BO', '').upper()
            ticker_symbol = f"{clean_symbol}.NS"
            ticker = yf.Ticker(ticker_symbol)
            data = ticker.history(period="5d")
            if data.empty:
                return None
            price = float(data["Close"].iloc[-1])
            print(f"✅ yfinance NSE fallback for {clean_symbol}: ₹{price}")
            return price
        except Exception as e:
            print(f"yfinance NSE fallback error for {symbol}: {e}")
            return None
    
    def get_bse_price(self, symbol: str, scrip_code: str = None) -> Optional[float]:
        try:
            # BSE stocks use .BO suffix in yfinance
            clean_symbol = symbol.replace('.NS', '').replace('.BSE', '').replace('.BO', '')
            ticker_symbol = f"{clean_symbol}.BO"
            
            print(f"Fetching {ticker_symbol} from yfinance...")
            
            ticker = yf.Ticker(ticker_symbol)
            data = ticker.history(period="5d")  # Get 5 days for reliability
            
            if not data.empty:
                price = data['Close'].iloc[-1]
                print(f"✅ BSE price for {clean_symbol} (via yfinance): ₹{price}")
                return float(price)
            else:
                print(f"❌ No BSE data for {clean_symbol} from yfinance")
                return None
                
        except Exception as e:
            print(f"BSE (yfinance) error for {symbol}: {e}")
            return None
    
    def _get_bse_scrip_code(self, symbol: str) -> Optional[str]:
        """
        Map common NSE symbols to BSE scrip codes
        This is a limited mapping - ideally fetch from database
        """
        # Common stock mappings
        BSE_SCRIP_CODES = {
            'RELIANCE': '500325',
            'TCS': '532540',
            'HDFCBANK': '500180',
            'INFY': '500209',
            'ICICIBANK': '532174',
            'HINDUNILVR': '500696',
            'ITC': '500875',
            'SBIN': '500112',
            'BHARTIARTL': '532454',
            'KOTAKBANK': '500247',
            'LT': '500510',
            'AXISBANK': '532215',
            'ASIANPAINT': '500820',
            'MARUTI': '532500',
            'TITAN': '500114',
            'SUNPHARMA': '524715',
            'WIPRO': '507685',
            'ULTRACEMCO': '532538',
            'NESTLEIND': '500790',
            'POWERGRID': '532898',
        }
        
        clean_symbol = symbol.replace('.NS', '').replace('.BSE', '').upper()
        return BSE_SCRIP_CODES.get(clean_symbol)
    
    def get_stock_price(self, symbol: str, exchange: str = "NSE") -> Optional[float]:
        """
        Get stock price from specified exchange
        
        Args:
            symbol: Stock symbol (e.g., 'RELIANCE')
            exchange: 'NSE' or 'BSE'
        
        Returns:
            Current price or None
        """
        if exchange.upper() == "BSE":
            # For BSE, try to get price
            price = self.get_bse_price(symbol)
            
            # Fallback to NSE if BSE fails
            if not price:
                print(f"BSE failed for {symbol}, trying NSE fallback")
                price = self.get_nse_price(symbol)
            if not price:
                print(f"NSE API fallback failed for {symbol}, trying yfinance NSE")
                price = self.get_yfinance_nse_price(symbol)
            
            return price
        else:
            # Policy: NSE first, then yfinance fallback
            price = self.get_nse_price(symbol)
            if price:
                return price
            print(f"NSE API failed for {symbol}, trying yfinance NSE fallback")
            return self.get_yfinance_nse_price(symbol)
    
    def get_multiple_prices(self, symbols: list, exchange: str = "NSE") -> dict:
        """Get prices for multiple symbols"""
        prices = {}
        
        for symbol in symbols:
            price = self.get_stock_price(symbol, exchange)
            if price:
                prices[symbol] = price
            time.sleep(0.5)  # Rate limiting
        
        return prices
