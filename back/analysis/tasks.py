from celery import shared_task
from django.utils import timezone
from datetime import datetime, timedelta
from analytics.models import MarketData, Coin
from redis_cache.cache_utils.market import MarketDataCache
import requests
import pandas as pd
import logging
import ta
from django.core.cache import cache
from typing import Optional, Dict, Any
from decimal import Decimal
from analysis.models import SentimentFeatures, TechnicalFeatures
from analytics.models import DailySentimentData
import numpy as np
import os

logger = logging.getLogger(__name__)


# -----------------------
# Helper Functions
# -----------------------

def compute_technical_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Convert Decimals to float for calculation
    for col in df.columns:
        if not df[col].empty and isinstance(df[col].iloc[0], Decimal):
            df[col] = df[col].astype(float)

    # ATR Lag 9
    df['prev_atr_lag9'] = df['atr'].shift(9)

    # MACD Signal Lag 4
    df['prev_macd_signal_lag4'] = df['macd_signal'].shift(4)

    # RSI Moving Average (5)
    df['prev_rsi_ma5'] = df['rsi'].rolling(window=5).mean().shift(1)

    # Bollinger Band Lower Lag 10
    df['prev_bb_lower_lag10'] = df['bb_lower'].shift(10)

    # MACD Histogram STD rolling
    df['prev_macd_hist_std8_ma'] = df['macd_hist'].rolling(8).std().shift(1)
    df['prev_macd_hist_std7_ma'] = df['macd_hist'].rolling(7).std().shift(1)

    # Williams %R MA7
    df['prev_williams_r_ma7'] = df['williams_r'].rolling(7).mean().shift(1)

    # Volume MA10
    df['volume_prev_ma10'] = df['volume'].rolling(10).mean().shift(1)

    # Quote Volume MA7/MA8
    df['prev_quote_volume_ma7'] = df['quote_volume'].rolling(7).mean().shift(1)
    df['prev_quote_volume_ma8'] = df['quote_volume'].rolling(8).mean().shift(1)

    # Close Price MA5
    df['prev_close_ma5'] = df['close_price'].rolling(5).mean().shift(1)

    # Taker Buy Base Volume STD MA7
    df['prev_taker_buy_base_volume_std7_ma'] = df['taker_buy_base_volume'].rolling(7).std().shift(1)

    # RSI STD 2 MA
    df['prev_rsi_std2_ma'] = df['rsi'].rolling(2).std().shift(1)

    # Taker Buy Quote Volume lag 10
    df['prev_taker_buy_quote_volume_lag10'] = df['taker_buy_quote_volume'].shift(10)

    # Price Change % features
    if 'price_change_percent_24h' in df.columns:
        base = df['price_change_percent_24h']
    else:
        base = df['close_price'].pct_change(2).shift(1) * 100
    
    df['2_periods_back_back_change_pct'] = base
    df['2_periods_back_back_change_pct_lag1'] = base.shift(1)
    df['2_periods_back_back_change_pct_lag4'] = base.shift(4)
    df['2_periods_back_back_change_pct_lag8'] = base.shift(8)

    return df


def compute_sentiment_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Base features from raw sentiment
    if 'sentiment_score' in df.columns:
        df['extremely_positive'] = (df['sentiment_score'] > 0.8).astype(int)
        df['extremely_negative'] = (df['sentiment_score'] < -0.8).astype(int)
        df['avg_sentiment'] = df['sentiment_score']
    
    if 'num_articles' not in df.columns:
        counts = ['bearish', 'bullish', 'extremely_bearish', 'extremely_bullish', 'neutral']
        # Ensure all count columns exist before summing
        for c in counts:
            if c not in df.columns:
                df[c] = 0
        df['num_articles'] = df[counts].sum(axis=1)

    # Rolling/lagging features
    df['prev_num_articles_ma1_10'] = df['num_articles'].rolling(10).mean().shift(1)
    df['prev_extremely_positive_count_ma1_5'] = df['extremely_positive'].rolling(5).sum().shift(1)
    df['prev_extremely_positive_count_ma1_4'] = df['extremely_positive'].rolling(4).sum().shift(1)
    df['prev_extremely_negative_count_lag5'] = df['extremely_negative'].shift(5)
    df['prev_extremely_negative_count_std1_9_ma'] = df['extremely_negative'].rolling(window=9, min_periods=2).std().shift(1).fillna(0.0)
    df['prev_avg_sentiment_std1_6_ma'] = df['avg_sentiment'].rolling(6).std().shift(1)
    df['avg_sentiment_news_prev_std5_ma'] = df['avg_sentiment'].rolling(5).std().shift(1)
    df['prev_avg_sentiment_lag4'] = df['avg_sentiment'].shift(4)
    df['prev_min_sentiment_lag10'] = df['avg_sentiment'].rolling(10).min().shift(1)
    df['prev_std_sentiment_lag1'] = df['avg_sentiment'].rolling(2).std().shift(1)
    df['prev_min_sentiment_lag1'] = df['avg_sentiment'].rolling(2).min().shift(1)
    df['prev_std_sentiment_lag3'] = df['avg_sentiment'].rolling(3).std().shift(1)
    df['prev_median_sentiment_lag8'] = df['avg_sentiment'].rolling(8).median().shift(1)

    return df

# -----------------------
# Celery Tasks
# -----------------------

@shared_task
def update_all_technical_features_for_symbol(symbol: str, market_data_id: int):
    """
    Fetches market history, computes technical features for the specified
    market_data_id, saves them, and returns the saved feature dictionary.
    """
    try:
        coin = Coin.objects.get(symbol=symbol.upper())
        target_record = MarketData.objects.get(id=market_data_id)
        
        # Fetch enough history to compute features for the target record
        qs = MarketData.objects.filter(
            symbol=coin, 
            close_time__lte=target_record.close_time
        ).order_by('close_time')

        if not qs.exists():
            return {"status": "error", "message": "No market data found"}

        df_full_history = pd.DataFrame.from_records(qs.values())
        df_with_features = compute_technical_features(df_full_history)

        # Get the feature row corresponding to our target market_data_id
        last_row_df = df_with_features[df_with_features['id'] == market_data_id]
        if last_row_df.empty:
            return {"status": "error", "message": f"Could not find features for market_data_id {market_data_id}"}

        last_row = last_row_df.iloc[0].to_dict()

        # Map DataFrame column names to Django model field names
        mapping = {
            'change_pct': '2_periods_back_back_change_pct',
            'change_pct_lag1': '2_periods_back_back_change_pct_lag1',
            'change_pct_lag4': '2_periods_back_back_change_pct_lag4',
            'change_pct_lag8': '2_periods_back_back_change_pct_lag8'
        }
        features_to_save = {}
        for field in TechnicalFeatures._meta.get_fields():
            if not field.is_relation:
                df_col_name = mapping.get(field.name, field.name)
                if df_col_name in last_row and pd.notna(last_row[df_col_name]):
                    features_to_save[field.name] = last_row[df_col_name]
        
        if 'id' in features_to_save: del features_to_save['id']

        TechnicalFeatures.objects.update_or_create(
            symbol=coin,
            timestamp_id=market_data_id,
            defaults={'record_timestamp': target_record.close_time, **features_to_save}
        )
        return {"status": "success", "features": features_to_save}

    except Exception as e:
        logger.error(f"Technical features error for {symbol}: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


@shared_task
def update_all_sentiment_features_for_symbol(symbol: str, market_data_id: int):
    """
    Fetches sentiment history, computes features, aligns to the specified
    market_data_id, saves them, and returns the saved feature dictionary.
    """
    try:
        coin = Coin.objects.get(symbol=symbol.upper())
        target_record = MarketData.objects.get(id=market_data_id)

        # Fetch sentiment data up to the target time
        sentiment_qs = DailySentimentData.objects.filter(
            symbol=coin, 
            timestamp__lte=target_record.close_time
        ).order_by('timestamp')

        if not sentiment_qs.exists():
            return {"status": "success", "features": {}} # No error, just no data

        df_sent_history = pd.DataFrame.from_records(sentiment_qs.values())
        df_with_features = compute_sentiment_features(df_sent_history)

        # Get the last row of sentiment features available at or before the target time
        last_row_df = df_with_features.tail(1)
        if last_row_df.empty:
            return {"status": "success", "features": {}}

        last_row = last_row_df.iloc[0].to_dict()

        features_to_save = {}
        for field in SentimentFeatures._meta.get_fields():
            if not field.is_relation and field.name in last_row and pd.notna(last_row[field.name]):
                features_to_save[field.name] = last_row[field.name]
        
        if 'id' in features_to_save: del features_to_save['id']

        SentimentFeatures.objects.update_or_create(
            symbol=coin,
            timestamp_id=market_data_id, # Align to the requested market data record
            defaults={'record_timestamp': target_record.close_time, **features_to_save}
        )
        return {"status": "success", "features": features_to_save}

    except Exception as e:
        logger.error(f"Sentiment features error for {symbol}: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}
