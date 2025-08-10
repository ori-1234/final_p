"""
Redis cache constants and timeouts
"""

# Cache timeouts (in seconds)
class CacheTimeout:
    SHORT = 60          # 1 minute
    MEDIUM = 300        # 5 minutes
    LONG = 3600         # 1 hour
    DAY = 86400        # 24 hours
    WEEK = 604800      # 7 days
    MONTH = 2592000    # 30 days

# Cache key prefixes
class CachePrefix:
    USER = "user:"
    MARKET = "market:"
    ANALYTICS = "analytics:"
    TASK = "task:"
    LOCK = "lock:"

# Cache key patterns
class CacheKeys:
    # User related keys
    USER_PROFILE = f"{CachePrefix.USER}profile:{{}}"
    USER_SETTINGS = f"{CachePrefix.USER}settings:{{}}"
    USER_PERMISSIONS = f"{CachePrefix.USER}permissions:{{}}"
    
    # Market related keys
    MARKET_DATA = f"{CachePrefix.MARKET}data:{{}}"
    MARKET_CHART = f"{CachePrefix.MARKET}chart:{{}}"
    MARKET_VOLUME = f"{CachePrefix.MARKET}volume:{{}}"
    
    # Analytics related keys
    ANALYSIS_DATA = f"{CachePrefix.ANALYTICS}analysis_data:{{}}"
    ANALYTICS_DAILY = f"{CachePrefix.ANALYTICS}daily:{{}}"
    ANALYTICS_WEEKLY = f"{CachePrefix.ANALYTICS}weekly:{{}}"
    ANALYTICS_MONTHLY = f"{CachePrefix.ANALYTICS}monthly:{{}}"
    
    # Task related keys
    TASK_STATUS = f"{CachePrefix.TASK}status:{{}}"
    TASK_RESULT = f"{CachePrefix.TASK}result:{{}}"
    TASK_LOCK = f"{CachePrefix.LOCK}task:{{}}"

    @staticmethod
    def format_key(pattern: str, *args) -> str:
        """Format a cache key with the given arguments"""
        return pattern.format(*args)

# Cache expiration times (in seconds)
class CacheExpiration:
    # Market Data
    MARKET_DATA = 3600  # 1 hour
    CHART_DATA = 86400  # 24 hours
    VOLUME_DATA = 3600  # 1 hour
    
