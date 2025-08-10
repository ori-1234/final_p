from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.utils import timezone
from datetime import timedelta
import logging
import asyncio
import os
from celery import chain
import pandas as pd
from django.db import transaction
from datetime import time

logger = logging.getLogger(__name__)

class AnalyticsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'analytics'

    def ready(self):
        # Connect to post_migrate signal
        post_migrate.connect(self.on_post_migrate, sender=self)
        logger.info("Connected on_post_migrate signal in AnalyticsConfig.ready()")
        
        # Initialize services
        try:
            if os.environ.get('RUN_MAIN'):  # Prevent duplicate execution in development
                self.initialize_services()
        except Exception as e:
            logger.error(f"Error in ready(): {str(e)}")

    def initialize_services(self):
        """Initialize all required services"""
        try:
            # Initialize WebSocket
            from .consumers import BinanceWebSocketConsumer
            from django.core.cache import cache
            
            # Clear existing cache
            cache.clear()
            logger.info("Cleared existing cache")

            # Initialize daily sentiment
            self.initialize_daily_sentiment()
            logger.info("Daily sentiment initialization completed")
            
            # First fetch historical data
            self.initialize_klines()
            logger.info("Historical data initialization completed")
            
            # Then initialize cache with the new data
            # self.initialize_cache()
            # logger.info("Cache initialization completed")
            
            # Finally start the WebSocket
            binance_ws_manager = BinanceWebSocketConsumer()
            binance_ws_manager.start()
            logger.info("WebSocket connection initialized")
            
        except Exception as e:
            logger.error(f"Error initializing services: {str(e)}")

    def initialize_daily_sentiment(self):
        """
        מריץ שרשרת משימות יומית לכל מטבע:
        - שליחת בקשת webhook ל-n8n (דרך Celery)
        - המתנה לסיום (ב-Celery, לא בשרת)
        - ביצוע אגרגציית סנטימנט
        - יצירת JSON מובנה
        """
        try:
            from .tasks import (
                fetch_news_sentiment_data,
            )
            import logging
            logger = logging.getLogger(__name__)
            logger.info("🚀 Starting full sentiment pipeline for all symbols (Celery chain)")

            # symbols = ['BTC']
            symbols = ['BTC', 'ETH', 'SOL', 'XRP', 'LTC']
            try:
                logger.info("➡️ Dispatching one chained pipeline for symbols in order: %s", symbols)
                task_chain = chain(*[fetch_news_sentiment_data.s(symbol) for symbol in symbols])
                task_chain.apply_async()
                logger.info("✅ Chained pipeline dispatched (sequential per symbol)")
            except Exception as e:
                logger.error("❌ Failed to dispatch chained pipeline: %s", e)
                # try:
                #     logger.info(f"➡️ Dispatching generate_structured_sentiment_json for {symbol}")
                #     generate_structured_sentiment_json.apply_async(args=[symbol])
                #     logger.info(f"✅ generate_structured_sentiment_json dispatched for {symbol}")
                # except Exception as e:
                #     logger.error(f"❌ generate_structured_sentiment_json failed for {symbol}: {e}")
                #     continue
            logger.info("✅ All sentiment pipelines (Celery chain) dispatched successfully")
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"❌ Error initializing daily sentiment pipeline: {e}")



    def initialize_klines(self):
        """
        Asynchronously triggers the Celery task to initialize historical 
        klines data for all coins.
        """
        from .tasks import fetch_missing_klines

        coins = ['BTC', 'ETH', 'SOL', 'XRP', 'LTC']

        logger.info("Queueing missing 12h klines updates via Celery...")

        for symbol in coins:
            try:
                fetch_missing_klines.delay(symbol)
                logger.info(f"Dispatched fetch_missing_klines for {symbol}")
            except Exception as e:
                logger.error(f"Failed to dispatch fetch_missing_klines for {symbol}: {e}")


    # def initialize_cache(self):
    #     """Initialize both market data and chart data cache"""
    #     try:
    #         from .models import Coin
    #         from .tasks import update_coin_details_cache, update_coin_volume_cache
    #         from redis_cache.cache_utils.market import MarketDataCache
            
    #         logger.info("Starting cache initialization")
            
    #         coins = Coin.objects.all()
    #         if not coins.exists():
    #             logger.warning("No coins found in database")
    #             return

    #         for coin in coins:
    #             try:
    #                 # Update chart data cache synchronously on startup
    #                 logger.info(f"Initializing chart data cache for {coin.symbol}")
    #                 cache_data = update_coin_details_cache(coin.symbol)
    #                 volume_cache_data = update_coin_volume_cache(coin.symbol)
                    
    #                 if cache_data:
    #                     logger.info(f"Successfully initialized chart data cache for {coin.symbol}")
    #                 else:
    #                     logger.error(f"Failed to initialize chart data cache for {coin.symbol}")
                    
    #                 if volume_cache_data:
    #                     logger.info(f"Successfully initialized volume data cache for {coin.symbol}")
    #                 else:
    #                     logger.error(f"Failed to initialize volume data cache for {coin.symbol}")

    #             except Exception as e:
    #                 logger.error(f"Error initializing cache for {coin.symbol}: {str(e)}")
    #                 continue

    #         logger.info("Cache initialization completed")

    #     except Exception as e:
    #         logger.error(f"Error in initialize_cache: {str(e)}")

    def on_post_migrate(self, **kwargs):
        logger.info("on_post_migrate signal triggered in AnalyticsConfig!")
