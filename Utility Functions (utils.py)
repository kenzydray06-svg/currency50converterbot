import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

class CurrencyConverter:
    """Handles currency conversion with caching"""
    
    def __init__(self, api_url: str = "https://api.exchangerate-api.com/v4/latest/"):
        self.api_url = api_url
        self.cache: Dict[str, Any] = {
            'data': None,
            'timestamp': None,
            'base': None
        }
        self.cache_duration = 3600  # 1 hour in seconds
        
    def _fetch_rates(self, base_currency: str = 'USD') -> Optional[Dict]:
        """Fetch exchange rates from API"""
        try:
            response = requests.get(f"{self.api_url}{base_currency}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Fetched rates for {base_currency}")
                return data
            else:
                logger.error(f"API error: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("API request timed out")
            return None
        except requests.exceptions.ConnectionError:
            logger.error("API connection error")
            return None
        except Exception as e:
            logger.error(f"API fetch error: {e}")
            return None
    
    def get_rates(self, base_currency: str = 'USD') -> Optional[Dict]:
        """Get exchange rates with caching"""
        current_time = datetime.now()
        
        # Check cache
        if (self.cache['data'] and 
            self.cache['timestamp'] and 
            self.cache['base'] == base_currency):
            
            elapsed = (current_time - self.cache['timestamp']).total_seconds()
            if elapsed < self.cache_duration:
                logger.debug(f"Using cached rates for {base_currency}")
                return self.cache['data']['rates']
        
        # Fetch new rates
        data = self._fetch_rates(base_currency)
        
        if data:
            self.cache['data'] = data
            self.cache['timestamp'] = current_time
            self.cache['base'] = base_currency
            return data['rates']
        
        # Return cached data if available
        if self.cache['data']:
            logger.warning("Using stale cache due to API failure")
            return self.cache['data']['rates']
        
        return None
    
    def convert(self, amount: float, from_currency: str, to_currency: str) -> Optional[float]:
        """Convert amount from one currency to another"""
        try:
            # Get rates
            rates = self.get_rates(from_currency)
            
            if not rates or to_currency not in rates:
                return None
            
            # Perform conversion
            result = amount * rates[to_currency]
            return round(result, 2)
            
        except Exception as e:
            logger.error(f"Conversion error: {e}")
            return None
    
    def is_valid_currency(self, currency_code: str) -> bool:
        """Check if currency code is valid"""
        rates = self.get_rates()
        return rates is not None and currency_code in rates
    
    def get_all_currencies(self) -> List[str]:
        """Get list of all supported currencies"""
        rates = self.get_rates()
        if rates:
            return list(rates.keys())
        return []
    
    def get_currency_info(self, currency_code: str) -> Optional[Dict]:
        """Get information about a currency"""
        # This could be extended with a currency database
        common_currencies = {
            'USD': {'name': 'US Dollar', 'symbol': '$'},
            'EUR': {'name': 'Euro', 'symbol': '€'},
            'GBP': {'name': 'British Pound', 'symbol': '£'},
            'JPY': {'name': 'Japanese Yen', 'symbol': '¥'},
            'CNY': {'name': 'Chinese Yuan', 'symbol': '¥'},
            'INR': {'name': 'Indian Rupee', 'symbol': '₹'},
            'CAD': {'name': 'Canadian Dollar', 'symbol': 'C$'},
            'AUD': {'name': 'Australian Dollar', 'symbol': 'A$'},
            'CHF': {'name': 'Swiss Franc', 'symbol': 'Fr'},
            'NZD': {'name': 'New Zealand Dollar', 'symbol': 'NZ$'},
        }
        return common_currencies.get(currency_code)

def format_amount(amount: float) -> str:
    """Format amount with thousands separator"""
    if amount == int(amount):
        return f"{amount:,.0f}"
    return f"{amount:,.2f}"

def get_currency_symbol(currency_code: str) -> str:
    """Get currency symbol"""
    symbols = {
        'USD': '$', 'EUR': '€', 'GBP': '£', 'JPY': '¥',
        'CNY': '¥', 'INR': '₹', 'CAD': 'C$', 'AUD': 'A$',
        'CHF': 'Fr', 'NZD': 'NZ$', 'KRW': '₩', 'RUB': '₽',
        'BRL': 'R$', 'MXN': '$', 'SGD': 'S$', 'HKD': 'HK$',
        'SEK': 'kr', 'NOK': 'kr', 'DKK': 'kr', 'PLN': 'zł',
        'TRY': '₺', 'THB': '฿', 'IDR': 'Rp', 'MYR': 'RM',
        'PHP': '₱', 'VND': '₫', 'AED': 'د.إ', 'SAR': 'ر.س',
        'ZAR': 'R', 'NGN': '₦', 'EGP': 'E£', 'KWD': 'KD',
    }
    return symbols.get(currency_code, '')
