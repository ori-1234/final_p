import json
import logging
from typing import Dict, Optional
from redis_cache.client import redis_client
from redis_cache.constants import CacheKeys, CacheTimeout

logger = logging.getLogger(__name__)

class UserProfileCache:
    """Cache implementation for user profile data"""
    
    @classmethod
    def set_user_data(cls, user_id: int, user_data: Dict) -> bool:
        """Cache user profile data"""
        try:
            key = CacheKeys.format_key(CacheKeys.USER_PROFILE, user_id)
            return redis_client.set_json(key, user_data, timeout=CacheTimeout.DAY)
        except Exception as e:
            logger.error(f"Cache set error for user {user_id} profile: {e}")
            return False
    
    @classmethod
    def get_user_data(cls, user_id: int) -> Optional[Dict]:
        """Get cached user profile data"""
        try:
            key = CacheKeys.format_key(CacheKeys.USER_PROFILE, user_id)
            return redis_client.get_json(key)
        except Exception as e:
            logger.error(f"Cache get error for user {user_id} profile: {e}")
            return None
    
    @classmethod
    def invalidate_user_data(cls, user_id: int) -> bool:
        """Invalidate cached profile data for a user"""
        try:
            key = CacheKeys.format_key(CacheKeys.USER_PROFILE, user_id)
            return bool(redis_client.redis_client.delete(key))
        except Exception as e:
            logger.error(f"Cache invalidation error for user {user_id} profile: {e}")
            return False

   