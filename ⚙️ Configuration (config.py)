import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration settings for the bot"""
    
    # Telegram Bot Token (required)
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
    
    # API Configuration
    CURRENCY_API_URL = os.getenv('CURRENCY_API_URL', 'https://api.exchangerate-api.com/v4/latest/')
    
    # Cache settings (in seconds)
    CACHE_DURATION = int(os.getenv('CACHE_DURATION', 3600))  # 1 hour
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Rate limit settings
    MAX_REQUESTS_PER_MINUTE = int(os.getenv('MAX_REQUESTS_PER_MINUTE', 30))
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.TELEGRAM_TOKEN:
            raise ValueError("TELEGRAM_TOKEN is not set")
        return True
