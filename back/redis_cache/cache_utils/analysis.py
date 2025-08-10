import logging
from typing import Dict, Optional
from redis_cache.client import redis_client
from redis_cache.constants import CacheKeys, CacheTimeout

logger = logging.getLogger(__name__)

class AnalysisDataCache:
    """Cache implementation for n8n analysis data"""

    @classmethod
    def set_analysis_data(cls, symbol: str, data: Dict) -> bool:
        """Set analysis data in cache for a given symbol."""
        try:
            key = CacheKeys.format_key(CacheKeys.ANALYSIS_DATA, symbol.lower())
            # Use a longer timeout as this data is generated less frequently
            return redis_client.set_json(key, data, timeout=CacheTimeout.DAY)
        except Exception as e:
            logger.error(f"Cache set error for analysis data (symbol: {symbol}): {e}")
            return False

    @classmethod
    def get_analysis_data(cls, symbol: str) -> Optional[Dict]:
        """Get analysis data from cache for a given symbol."""
        try:
            key = CacheKeys.format_key(CacheKeys.ANALYSIS_DATA, symbol.lower())
            return redis_client.get_json(key)
        except Exception as e:
            logger.error(f"Cache get error for analysis data (symbol: {symbol}): {e}")
            return None

    @classmethod
    def delete_analysis_data(cls, symbol: str) -> bool:
        """Delete analysis data from cache for a given symbol."""
        try:
            key = CacheKeys.format_key(CacheKeys.ANALYSIS_DATA, symbol.lower())
            deleted_count = redis_client.delete(key)
            logger.info(f"Deleted analysis data cache for {symbol}. Keys deleted: {deleted_count}")
            return deleted_count > 0
        except Exception as e:
            logger.error(f"Cache delete error for analysis data (symbol: {symbol}): {e}")
            return False
