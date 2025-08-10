from celery import shared_task
from .models import MarketData, Coin
from redis_cache.cache_utils.market import MarketDataCache
import requests
import logging
from django.db import transaction
import ta
from typing import Optional, Dict, Any, Union
from decimal import Decimal
from django.conf import settings
from datetime import time
import pandas as pd
import numpy as np
import ta
from django.utils import timezone
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)

class BinanceInterval(str, Enum):
    """Binance kline/candlestick intervals"""
    MINUTE_1 = '1m'
    MINUTE_3 = '3m'
    MINUTE_5 = '5m'
    MINUTE_15 = '15m'
    MINUTE_30 = '30m'
    HOUR_1 = '1h'
    HOUR_2 = '2h'
    HOUR_4 = '4h'
    HOUR_6 = '6h'
    HOUR_8 = '8h'
    HOUR_12 = '12h'
    DAY_1 = '1d'
    DAY_3 = '3d'
    WEEK_1 = '1w'
    MONTH_1 = '1M'


def fetch_binance_candles(
    symbol: str,
    interval: Union[str, BinanceInterval],
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = 1000
) -> Optional[pd.DataFrame]:
    """
    Fetch candlestick data from Binance API with flexible parameters.
    """
    import requests
    
    base_url = 'https://api.binance.com/api/v3/klines'
    formatted_symbol = f"{symbol.upper()}USDT"
    
    # Validate interval
    if isinstance(interval, str):
        try:
            interval = BinanceInterval(interval)
        except ValueError:
            valid_intervals = [i.value for i in BinanceInterval]
            logger.error(f"Invalid interval: {interval}. Valid intervals: {valid_intervals}")
            return None
    
    params = {
        'symbol': formatted_symbol,
        'interval': interval.value,
        'limit': min(limit, 1000),  # Binance maximum is 1000
        'timeZone' : 3
    }
    
    # Add timestamps if provided
    if start_time:
        params['startTime'] = int(start_time.timestamp() * 1000)
    if end_time:
        params['endTime'] = int(end_time.timestamp() * 1000)

    all_data = []
    retry_count = 0
    max_retries = 3

    while retry_count < max_retries:
        try:
            while True:
                response = requests.get(base_url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()

                if not data:
                    break

                all_data.extend(data)
                
                # Update start time to fetch next batch
                last_close_time = data[-1][6]  # Close time from last candle
                params['startTime'] = last_close_time + 1

                # Stop if we've reached the end time or limit
                if end_time and params['startTime'] >= int(end_time.timestamp() * 1000):
                    break
                if len(all_data) >= limit:
                    all_data = all_data[:limit]
                    break

            if not all_data:
                logger.warning(f"No data returned for {symbol}")
                return None

            # Create DataFrame with proper column names
            df = pd.DataFrame(all_data, columns=[
                'open_time', 'open_price', 'high_price', 'low_price', 'close_price', 
                'volume', 'close_time', 'quote_volume', 'num_trades',
                'taker_buy_base', 'taker_buy_quote', 'ignore'
            ])

            # Convert timestamps to datetime - simple naive datetime as Binance provides
            df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
            df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
            
            # Convert numeric columns to float before any processing
            numeric_columns = [
                'open_price', 'high_price', 'low_price', 'close_price', 'volume',
                'quote_volume', 'num_trades', 'taker_buy_base', 'taker_buy_quote'
            ]
            df[numeric_columns] = df[numeric_columns].astype(float)

            # Drop the 'ignore' column as it's not needed
            df = df.drop('ignore', axis=1)

            return df

        except requests.exceptions.RequestException as e:
            retry_count += 1
            logger.warning(f"Retry {retry_count} for {symbol}: {str(e)}")
            if retry_count == max_retries:
                logger.error(f"Max retries reached for {symbol}: {str(e)}")
                return None
        except Exception as e:
            logger.error(f"Error fetching candles for {symbol}: {str(e)}")
            return None

def fetch_historical_data_from_binance(symbol: str) -> Optional[pd.DataFrame]:
    """Fetch 12-hour candles from the last saved record up to now for the given symbol.

    If the coin has no data yet, defaults to the last 7 days.
    Ensures `open_time`/`close_time` are tz-aware UTC.
    """
    try:
        symbol_upper = symbol.upper()

        latest_record = (
            MarketData.objects.filter(symbol__symbol=symbol_upper)
            .order_by("-close_time")
            .first()
        )

        if latest_record:
            start_time = latest_record.close_time + timedelta(milliseconds=1)
        else:
            start_time = timezone.now() - timedelta(days=7)

        end_time = timezone.now()
        logger.info(
            f"Fetching historical data for {symbol_upper} from {start_time} to {end_time}"
        )

        df = fetch_binance_candles(
            symbol=symbol_upper,
            interval=BinanceInterval.HOUR_12,
            start_time=start_time,
            end_time=end_time,
        )

        if df is None or df.empty:
            logger.error(f"No data returned for {symbol_upper}")
            return None

        # Ensure timestamps are tz-aware UTC
        for time_col in ["open_time", "close_time"]:
            if pd.api.types.is_datetime64_any_dtype(df[time_col]):
                if getattr(df[time_col].dt, "tz", None) is None:
                    df[time_col] = df[time_col].dt.tz_localize("UTC")
            else:
                df[time_col] = pd.to_datetime(df[time_col], utc=True)

        logger.info(f"Successfully fetched {len(df)} 12h candles for {symbol_upper}")
        return df

    except Exception as e:
        logger.error(f"Error in fetch_historical_data_from_binance: {str(e)}")
        return None
    

def get_history_for_indicators(coin: Coin) -> pd.DataFrame:
    """
    מביא היסטוריה לפני תחילת ה-new_df לחישוב אינדיקטורים.
    מניח שאין חוסר מידע ולכן לא משלים מבינאנס.
    """
    qs = (
        MarketData.objects
        .filter(symbol=coin)
        .order_by('-open_time')[:30]
    )
    return pd.DataFrame.from_records(qs.values())



def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    מחשב אינדיקטורים טכניים + אחוז שינוי 24h (ל־12h קנדלים -> shift(2)).
    """
    if df is None or df.empty:
        return df

    df = df.copy().sort_values("close_time").reset_index(drop=True)

    # טיפוסים נומריים
    num_cols = ["open_price", "high_price", "low_price", "close_price", "volume"]
    for c in num_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").astype(float)

    # RSI
    try:
        df["RSI"] = ta.momentum.RSIIndicator(close=df["close_price"], window=14).rsi()
    except Exception:
        df["RSI"] = np.nan

    # MACD
    try:
        # EWMA ישיר: בלי חוסרים בתחילת הסדרה
        ema_fast = df["close_price"].ewm(span=12, adjust=False, min_periods=1).mean()
        ema_slow = df["close_price"].ewm(span=26, adjust=False, min_periods=1).mean()
        df["MACD"] = ema_fast - ema_slow
        df["MACD_Signal"] = df["MACD"].ewm(span=9, adjust=False, min_periods=1).mean()
        df["MACD_Hist"] = df["MACD"] - df["MACD_Signal"]
    except Exception:
        df["MACD"] = np.nan
        df["MACD_Signal"] = np.nan
        df["MACD_Hist"] = np.nan


    # Bollinger Bands
    try:
        bb = ta.volatility.BollingerBands(close=df["close_price"], window=20, window_dev=2)
        df["BB_Upper"]  = bb.bollinger_hband()
        df["BB_Middle"] = bb.bollinger_mavg()
        df["BB_Lower"]  = bb.bollinger_lband()
    except Exception:
        df["BB_Upper"] = df["BB_Middle"] = df["BB_Lower"] = np.nan

    # ATR
    try:
        df["ATR"] = ta.volatility.AverageTrueRange(
            high=df["high_price"], low=df["low_price"], close=df["close_price"], window=14
        ).average_true_range()
    except Exception:
        df["ATR"] = np.nan

    # Williams %R
    try:
        df["Williams_R"] = ta.momentum.WilliamsRIndicator(
            high=df["high_price"], low=df["low_price"], close=df["close_price"], lbp=14
        ).williams_r()
    except Exception:
        df["Williams_R"] = np.nan

    # אחוז שינוי 24 שעות (בקנדלים 12h -> shift(2))
    prev_close_24h = df["close_price"].shift(2)
    with np.errstate(invalid="ignore", divide="ignore"):
        df["price_change_percent_24h"] = (
            (df["close_price"] - prev_close_24h) / prev_close_24h * 100.0
        ).replace([np.inf, -np.inf], np.nan)

    return df




def process_and_save_data(symbol: str, df: pd.DataFrame) -> bool:
    """
    שומר נתוני שוק ל-DB ב-bulk. מניח שהאינדיקטורים כבר חושבו ב-df.
    """
    if df is None or df.empty:
        logger.info(f"No rows to save for {symbol}")
        return True

    try:
        try:
            coin = Coin.objects.get(symbol=symbol.upper())
        except Coin.DoesNotExist:
            logger.error(f"Coin {symbol} not found in database")
            return False

        df = df.copy().sort_values("close_time").reset_index(drop=True)

        # טיפוסים נומריים
        numeric_columns = [
            "open_price", "high_price", "low_price", "close_price", "volume",
            "quote_volume", "num_trades", "taker_buy_base", "taker_buy_quote",
            "price_change_percent_24h", "rsi", "macd", "macd_signal", "macd_hist",
            "bb_upper", "bb_middle", "bb_lower", "atr", "williams_r",
        ]
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        def fsafe(x):
            return float(x) if pd.notna(x) else None

        def isafe(x):
            try:
                return int(x) if pd.notna(x) else 0
            except Exception:
                return 0

        bulk = []
        for row in df.itertuples(index=False):
            market_data = MarketData(
                symbol=coin,
                open_time=getattr(row, "open_time", None),
                close_time=getattr(row, "close_time", None),
                open_price=fsafe(getattr(row, "open_price", None)),
                high_price=fsafe(getattr(row, "high_price", None)),
                low_price=fsafe(getattr(row, "low_price", None)),
                close_price=fsafe(getattr(row, "close_price", None)),
                volume=fsafe(getattr(row, "volume", None)),
                quote_volume=fsafe(getattr(row, "quote_volume", None)),
                num_trades=isafe(getattr(row, "num_trades", None)),
                taker_buy_base_volume=fsafe(getattr(row, "taker_buy_base", None)),
                taker_buy_quote_volume=fsafe(getattr(row, "taker_buy_quote", None)),
                price_change_percent_24h=(
                    round(fsafe(getattr(row, "price_change_percent_24h", None)), 2)
                    if pd.notna(getattr(row, "price_change_percent_24h", np.nan)) else None
                ),
                rsi=(
                    round(fsafe(getattr(row, "RSI", None)), 2)
                    if pd.notna(getattr(row, "RSI", np.nan)) else None
                ),
                macd=fsafe(getattr(row, "MACD", None)) if pd.notna(getattr(row, "MACD", np.nan)) else None,
                macd_signal=fsafe(getattr(row, "MACD_Signal", None)) if pd.notna(getattr(row, "MACD_Signal", np.nan)) else None,
                macd_hist=fsafe(getattr(row, "MACD_Hist", None)) if pd.notna(getattr(row, "MACD_Hist", np.nan)) else None,
                bb_upper=fsafe(getattr(row, "BB_Upper", None)) if pd.notna(getattr(row, "BB_Upper", np.nan)) else None,
                bb_middle=fsafe(getattr(row, "BB_Middle", None)) if pd.notna(getattr(row, "BB_Middle", np.nan)) else None,
                bb_lower=fsafe(getattr(row, "BB_Lower", None)) if pd.notna(getattr(row, "BB_Lower", np.nan)) else None,
                atr=fsafe(getattr(row, "ATR", None)) if pd.notna(getattr(row, "ATR", np.nan)) else None,
                williams_r=fsafe(getattr(row, "Williams_R", None)) if pd.notna(getattr(row, "Williams_R", np.nan)) else None,
            )
            bulk.append(market_data)

        if bulk:
            with transaction.atomic():
                MarketData.objects.bulk_create(
                    bulk, batch_size=100, ignore_conflicts=True
                )
            logger.info(f"Saved {len(bulk)} records for {symbol}")

        total = MarketData.objects.filter(symbol=coin).count()
        logger.info(f"Total records for {symbol}: {total}")
        return True

    except Exception as e:
        logger.error(f"Error in process_and_save_data for {symbol}: {str(e)}", exc_info=True)
        return False

    

@shared_task
def fetch_missing_klines(symbol: Optional[str] = None) -> None:
    """
    Fetch and save missing 12-hour klines:
      1) משיכה מבינאנס של נרות חסרים
      2) משיכה מה-DB של 30 רשומות אחרונות (לחימום אינדיקטורים)
      3) איחוד (30 עבר + חדשות)
      4) חישוב אינדיקטורים על המסגרת המלאה
      5) שמירה ל-DB רק של הרשומות החדשות
    """
    coins = (
        Coin.objects.filter(symbol=symbol.upper())
        if symbol else Coin.objects.exclude(symbol__in=["USD", "USDC"])
    )

    for coin in coins:
        try:
            # (1) נרות חסרים מבינאנס (מאחרון close_time ועד עכשיו)
            df_new = fetch_historical_data_from_binance(coin.symbol)
            if df_new is None or df_new.empty:
                logger.info(f"No new data for {coin.symbol}")
                continue

            # בדיקת עמודות נדרשות
            required_columns = [
                "open_time", "close_time", "open_price", "high_price",
                "low_price", "close_price", "volume", "quote_volume",
                "num_trades", "taker_buy_base", "taker_buy_quote",
            ]
            missing = [c for c in required_columns if c not in df_new.columns]
            if missing:
                logger.error(f"Missing required columns for {coin.symbol}: {missing}")
                continue

            # (2) 30 רשומות היסטוריות אחרונות מה-DB (כבר עם אינדיקטורים)
            history_df = get_history_for_indicators(coin)
            # לא נוגעים ב-tz כאן לפי בקשתך

            # (3) איחוד: 30 עבר + חדשות
            full_df = pd.concat([history_df, df_new], ignore_index=True, sort=False)
            full_df = full_df.sort_values("close_time").reset_index(drop=True)

            # (4) חישוב אינדיקטורים (וגם price_change_percent_24h) על כל המסגרת,
            # כדי שהשורה/ות החדשות יקבלו ערכים נכונים בעזרת ההיסטוריה
            full_df = calculate_technical_indicators(full_df)

            # (5) שמירה: רק שורות חדשות (מאז המינימום של open_time החדשות)
            min_new_open = df_new["open_time"].min()
            new_df_to_save = full_df[full_df["open_time"] >= min_new_open].copy()

            logger.info(f"New data to save for {coin.symbol}: {len(new_df_to_save)}")
            if new_df_to_save.empty:
                logger.info(f"No new data to save for {coin.symbol}")
                continue

            success = process_and_save_data(coin.symbol, new_df_to_save)
            if success:
                logger.info(f"Updated {coin.symbol} with {len(new_df_to_save)} new records")
            else:
                logger.error(f"Failed to save data for {coin.symbol}")

        except Exception as e:
            logger.error(f"Error processing {coin.symbol}: {e}", exc_info=True)



#-----------------------------------------------------------------------------------------------------------------------------

@shared_task
def update_coin_details_cache(symbol: str) -> Optional[Dict[str, Any]]:
    """
    Update cache for a specific coin with daily (1 data point per day) 
    price data. We group by each calendar day and choose the last close_price
    for that day, similar to CoinGecko's daily historical approach.
    """
    try:
        logger.info(f"Starting chart data update for {symbol}")

        coin = Coin.objects.get(symbol=symbol.upper())

        latest_record = MarketData.objects.filter(symbol=coin).order_by('-close_time').first()
        if not latest_record:
            logger.warning(f"No market data found for {symbol}. Skipping.")
            return None

        end_date = latest_record.close_time

        timeframes = [7, 30, 60, 90, 120, 365]
        chart_data = {}

        for days in timeframes:
            start_date = end_date - timezone.timedelta(days=days)

            # Fetch all records in [start_date, end_date] ascending
            records = (
                MarketData.objects
                .filter(symbol=coin, close_time__gte=start_date, close_time__lte=end_date)
                .order_by('close_time')
                .values('close_time', 'close_price')
            )

            # Group by date, picking the final close_time per day
            daily_map = {}
            for r in records:
                if not r['close_price']: 
                    continue

                day_key = r['close_time'].date()
                if day_key not in daily_map or r['close_time'] > daily_map[day_key]['close_time']:
                    daily_map[day_key] = {
                        'close_time': r['close_time'],
                        'close_price': float(r['close_price'])
                    }

            # Build daily data (ts, price)
            daily_data = []
            for day_key in sorted(daily_map.keys()):
                rec = daily_map[day_key]
                ts = int(rec['close_time'].timestamp() * 1000)
                daily_data.append([ts, rec['close_price']])

            # Note: we changed the log message here
            logger.info(f"Timeframe {days}d -> {len(daily_data)} daily points for {symbol}")
            chart_data[str(days)] = daily_data

        cache_data = {"chart_data": chart_data}
        MarketDataCache.set_chart_data(symbol, cache_data)
        logger.info(f"Successfully cached chart data for {symbol}")

        return cache_data

    except Coin.DoesNotExist:
        logger.error(f"Coin {symbol} does not exist.")
        return None
    except Exception as e:
        logger.error(f"Error updating chart data cache for {symbol}: {e}")
        return None


@shared_task
def update_coin_volume_cache(symbol: str) -> Optional[Dict[str, Any]]:
    """
    Update cache for a specific coin with daily (1 data point per day) 
    volume data. We group by each calendar day and aggregate the total volume
    for that day, providing historical volume analysis.
    """
    try:
        logger.info(f"Starting volume data update for {symbol}")

        coin = Coin.objects.get(symbol=symbol.upper())

        latest_record = MarketData.objects.filter(symbol=coin).order_by('-close_time').first()
        if not latest_record:
            logger.warning(f"No market data found for {symbol}. Skipping.")
            return None

        end_date = latest_record.close_time

        timeframes = [7, 30, 60, 90, 120, 365]
        volume_data = {}

        for days in timeframes:
            start_date = end_date - timezone.timedelta(days=days)

            # Fetch all records in [start_date, end_date] ascending
            records = (
                MarketData.objects
                .filter(symbol=coin, close_time__gte=start_date, close_time__lte=end_date)
                .order_by('close_time')
                .values('close_time', 'volume')
            )

            # Group by date, summing the volume per day - FIX: use string representation of date as key
            daily_map = {}
            for r in records:
                if not r['volume']:
                    continue

                # Convert date to string format to use as dictionary key
                day_key = r['close_time'].date().isoformat()
                
                if day_key not in daily_map:
                    daily_map[day_key] = {
                        'total_volume': Decimal('0'),
                        'close_time': r['close_time']
                    }
                
                daily_map[day_key]['total_volume'] += Decimal(str(r['volume']))
                
                # Keep track of the latest timestamp for that day
                if r['close_time'] > daily_map[day_key]['close_time']:
                    daily_map[day_key]['close_time'] = r['close_time']

            # Build daily data (ts, volume)
            daily_data = []
            for day_key in sorted(daily_map.keys()):
                rec = daily_map[day_key]
                ts = int(rec['close_time'].timestamp() * 1000)
                daily_data.append([ts, float(rec['total_volume'])])

            logger.info(f"Timeframe {days}d -> {len(daily_data)} daily volume points for {symbol}")
            volume_data[str(days)] = daily_data

        cache_data = {"volume_data": volume_data}
        MarketDataCache.set_volume_data(symbol, cache_data)
        logger.info(f"Successfully cached volume data for {symbol}")

        return cache_data

    except Coin.DoesNotExist:
        logger.error(f"Coin {symbol} does not exist.")
        return None
    except Exception as e:
        logger.error(f"Error updating volume data cache for {symbol}: {e}")
        return None


@shared_task
def update_all_coin_details():
    """
    Update cache for all active coins.
    Runs on server startup and once daily at midnight.
    """
    try:
        logger.info("Starting full update of coin details")
        coins = Coin.objects.exclude(symbol__in=['USD', 'USDC'])
        
        if not coins.exists():
            logger.warning("No coins found in database")
            return
            
        for coin in coins:
            try:
                # Run update synchronously since this is a daily task
                update_coin_details_cache(coin.symbol)
                logger.info(f"Updated data for {coin.symbol}")
            except Exception as e:
                logger.error(f"Error updating {coin.symbol}: {str(e)}")
                continue
                
        logger.info("Completed full update of coin details")
                
    except Exception as e:
        logger.error(f"Error in update_all_coin_details: {str(e)}")
 

@shared_task
def fetch_news_sentiment_data(ticker_symbol=None):
    """
    Sends a POST request to the n8n webhook for all symbols in one request (or for a single symbol if provided), and only logs.
    Does not save to the database (the flow saves).
    """
    n8n_url = settings.N8N_SENTIMENT_ANALYSIS_URL
    try:
        # When running inside Docker, 'localhost' points to the current container.
        # Rewrite to the Docker service hostname so backend/celery can reach n8n.
        from urllib.parse import urlparse, urlunparse
        parsed = urlparse(n8n_url)
        if parsed.hostname in ("localhost", "127.0.0.1"):
            port = parsed.port or 5678
            n8n_url = urlunparse(parsed._replace(netloc=f"n8n:{port}"))
    except Exception:
        pass
    # If a specific symbol provided, send just that one
    if ticker_symbol:
        payload = {"Ticker_symbol": ticker_symbol}
        logger.info(f"📤 Sending single symbol: {ticker_symbol}")
        try:
            response = requests.post(n8n_url, json=payload, timeout=15)
            if not response.ok:
                logger.error(f"❌ Non-OK from n8n: {response.status_code} {response.text}")
                response.raise_for_status()
            logger.info(f"✅ n8n response: {response.json()}")
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error sending request: {e}")
            raise
        return

    # Otherwise loop over all active coins
    from analytics.models import Coin
    symbols = list(
        Coin.objects.filter(is_active=True).values_list('symbol', flat=True)
    )
    logger.info(f"📤 Dispatching sentiment fetch for {len(symbols)} symbols: {symbols}")

    for sym in symbols:
        payload = {"Ticker_symbol": sym}
        try:
            response = requests.post(n8n_url, json=payload, timeout=15)
            if not response.ok:
                logger.error(f"❌ Non-OK from n8n for {sym}: {response.status_code} {response.text}")
                continue
            logger.info(f"✅ n8n response for {sym}: {response.json()}")
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error sending request for {sym}: {e}")
            continue


@shared_task
def initialize_all_coins_historical_data():
    """
    Celery task to initialize historical klines data for all coins.
    This is intended to be called on application startup.
    """
    try:
        from django.db import connection

        logger.info("Starting historical klines initialization task")
        
        now = timezone.now()
        coins = Coin.objects.exclude(symbol__in=['USD', 'USDC'])

        for coin in coins:
            try:
                latest_record = MarketData.objects.filter(
                    symbol=coin
                ).order_by('-close_time').first()

                start_time = None
                if latest_record:
                    last_close = latest_record.close_time
                    # Ensure last_close is timezone aware
                    if last_close.tzinfo is None:
                        last_close = timezone.make_aware(last_close, timezone=timezone.utc)
                    
                    if last_close.time() < time(12, 0):
                        start_time = last_close.replace(hour=12, minute=0, second=0, microsecond=0)
                    else:
                        start_time = (last_close + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
                    
                    if start_time > now:
                        logger.info(f"Data for {coin.symbol} is up to date. No new klines to fetch.")
                        continue
                else:
                    start_time = now - timedelta(days=7)
                    if start_time.hour < 12:
                        start_time = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
                    else:
                        start_time = start_time.replace(hour=12, minute=0, second=0, microsecond=0)

                logger.info(f"Fetching historical klines for {coin.symbol} from {start_time} to {now}")
                
                df = fetch_binance_candles(coin.symbol, BinanceInterval.HOUR_12, start_time, now)
                
                if df is not None and not df.empty:
                    # Ensure timestamps are UTC aware
                    df['open_time'] = pd.to_datetime(df['open_time'], utc=True)
                    df['close_time'] = pd.to_datetime(df['close_time'], utc=True)
                    
                    # Validate that we have the required columns
                    required_columns = ['open_price', 'high_price', 'low_price', 'close_price', 'volume']
                    missing_columns = [col for col in required_columns if col not in df.columns]
                    if missing_columns:
                        logger.error(f"Missing required columns for {coin.symbol}: {missing_columns}")
                        continue
                    
                    full_df = get_history_for_indicators(coin, df, window=60)
                    
                    if full_df.empty:
                        logger.warning(f"No valid data for indicators calculation for {coin.symbol}")
                        continue
                    
                    full_df_with_indicators = calculate_technical_indicators(full_df)
                    full_df_with_indicators['price_change_percent_24h'] = (full_df_with_indicators['close_price'].pct_change(periods=2) * 100)
                    new_df_to_save = full_df_with_indicators[full_df_with_indicators['open_time'] >= df['open_time'].min()].copy()
                    
                    if not new_df_to_save.empty:
                        success = process_and_save_data(coin.symbol, new_df_to_save)
                        if success:
                            logger.info(f"Successfully processed historical data for {coin.symbol}")
                        else:
                            logger.error(f"Failed to save historical data for {coin.symbol}")
                    else:
                        logger.info(f"No new data to save for {coin.symbol}")
                else:
                    logger.warning(f"No historical data available for {coin.symbol}")
            
            except Exception as e:
                logger.error(f"Error processing historical data for {coin.symbol}: {str(e)}", exc_info=True)
                continue
            finally:
                connection.close()

        logger.info("Historical klines initialization task completed")

    except Exception as e:
        logger.error(f"Fatal error in initialize_all_coins_historical_data task: {str(e)}", exc_info=True)

