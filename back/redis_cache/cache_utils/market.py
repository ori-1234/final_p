import json
import logging
from typing import Dict, Optional
from redis_cache.client import redis_client
from redis_cache.constants import CacheKeys, CacheTimeout

logger = logging.getLogger(__name__)

class MarketDataCache:
    """Cache implementation for market data"""
    
    @classmethod 
    def set_market_data(cls, symbol: str, data: Dict) -> bool:
        """Set market data in cache"""
        try:
            key = CacheKeys.format_key(CacheKeys.MARKET_DATA, symbol.lower())
            return redis_client.set_json(key, data, timeout=CacheTimeout.MEDIUM)
        except Exception as e:
            logger.error(f"Cache set error for {symbol}: {e}")
            return False

    @classmethod
    def get_market_data(cls, symbol: str) -> Optional[Dict]:
        """Get market data from cache"""
        try:
            key = CacheKeys.format_key(CacheKeys.MARKET_DATA, symbol.lower())
            return redis_client.get_json(key)
        except Exception as e:
            logger.error(f"Cache get error for {symbol}: {e}")
            return None

    @classmethod
    def set_chart_data(cls, symbol: str, data: Dict) -> bool:
        """Set chart data in cache"""
        try:
            key = CacheKeys.format_key(CacheKeys.MARKET_CHART, symbol.lower())
            return redis_client.set_json(key, data, timeout=CacheTimeout.DAY)
        except Exception as e:
            logger.error(f"Cache set error for chart data {symbol}: {e}")
            return False

    @classmethod
    def get_chart_data(cls, symbol: str) -> Optional[Dict]:
        """Get chart data from cache"""
        try:
            key = CacheKeys.format_key(CacheKeys.MARKET_CHART, symbol.lower())
            return redis_client.get_json(key)
        except Exception as e:
            logger.error(f"Cache get error for chart data {symbol}: {e}")
            return None

    @classmethod
    def set_volume_data(cls, symbol: str, data: Dict) -> bool:
        """Set volume data in cache"""
        try:
            key = CacheKeys.format_key(CacheKeys.MARKET_VOLUME, symbol.lower())
            return redis_client.set_json(key, data, timeout=CacheTimeout.DAY)
        except Exception as e:
            logger.error(f"Cache set error for volume data {symbol}: {e}")
            return False

    @classmethod
    def get_volume_data(cls, symbol: str) -> Optional[Dict]:
        """Get volume data from cache"""
        try:
            key = CacheKeys.format_key(CacheKeys.MARKET_VOLUME, symbol.lower())
            return redis_client.get_json(key)
        except Exception as e:
            logger.error(f"Cache get error for volume data {symbol}: {e}")
            return None

    @classmethod
    def delete_chart_data(cls, symbol):
        """
        Delete chart data from cache
        
        Args:
            symbol (str): Coin symbol (e.g., 'BTC')
        """
        try:
            key = CacheKeys.format_key(CacheKeys.MARKET_CHART, symbol.lower())
            redis_client.delete(key)
            logger.debug(f"Deleted chart data cache for {symbol}")
        except Exception as e:
            logger.error(f"Cache delete error for chart data {symbol}: {e}")

    @classmethod
    def delete_volume_data(cls, symbol):
        """
        Delete volume data from cache
        
        Args:
            symbol (str): Coin symbol (e.g., 'BTC')
        """
        try:
            key = CacheKeys.format_key(CacheKeys.MARKET_VOLUME, symbol.lower())
            redis_client.delete(key)
            logger.debug(f"Deleted volume data cache for {symbol}")
        except Exception as e:
            logger.error(f"Cache delete error for volume data {symbol}: {e}")

 