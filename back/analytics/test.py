import os
import sys
import django
import pandas as pd
import numpy as np
import ta
import logging
from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta
from typing import Optional, List, Union
from enum import Enum
from django.utils.timezone import is_aware, make_aware

# 1) Make sure Python can see the root folder
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

# 2) Point to Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# 3) Now initialize Django
django.setup()

# 4) Now that Django is set up, you can safely import your models
from analytics.models import Coin, MarketData

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

def fetch_historical_data_from_binance(symbol: str, start_time: datetime, end_time: datetime) -> Optional[pd.DataFrame]:
    """
    Fetch historical data from Binance API using 12-hour intervals.
    """
    try:
        logger.info(f"Fetching historical data for {symbol} from {start_time} to {end_time}")
        
        # Fetch 12-hour candles for more granular data
        df = fetch_binance_candles(
            symbol=symbol,
            interval=BinanceInterval.HOUR_12,
            start_time=start_time,
            end_time=end_time
        )
        
        if df is None or df.empty:
            logger.error(f"No data returned for {symbol}")
            return None
            
        logger.info(f"Successfully fetched {len(df)} 12h candles for {symbol}")
        return df

    except Exception as e:
        logger.error(f"Error in fetch_historical_data_from_binance: {str(e)}")
        return None

def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate technical indicators for market data."""
    try:
        df = df.sort_values('close_time')
        
        # Calculate RSI
        rsi = ta.momentum.RSIIndicator(df['close_price'], window=14).rsi()
        
        # Calculate MACD
        macd = ta.trend.MACD(df['close_price'], window_fast=12, window_slow=26, window_sign=9)
        df['MACD'] = macd.macd()
        df['MACD_Signal'] = macd.macd_signal()
        df['MACD_Hist'] = macd.macd_diff()
        
        # Calculate Bollinger Bands
        bb = ta.volatility.BollingerBands(df['close_price'], window=20, window_dev=2)
        df['BB_Upper'] = bb.bollinger_hband()
        df['BB_Middle'] = bb.bollinger_mavg()
        df['BB_Lower'] = bb.bollinger_lband()
        
        # Calculate ATR (Average True Range)
        atr = ta.volatility.AverageTrueRange(
            high=df['high_price'], 
            low=df['low_price'], 
            close=df['close_price'], 
            window=14
        ).average_true_range()
        
        # Calculate Williams %R
        williams_r = ta.momentum.WilliamsRIndicator(
            high=df['high_price'],
            low=df['low_price'],
            close=df['close_price'],
            lbp=14
        ).williams_r()
        
        df['RSI'] = rsi
        df['ATR'] = atr
        df['Williams_R'] = williams_r
        
        return df

    except Exception as e:
        logger.error(f"Error calculating technical indicators: {str(e)}")
        return df

def process_and_save_data(symbol: str, df: pd.DataFrame) -> bool:
    """Process and save market data to database."""
    try:
        # Get coin instance
        try:
            coin = Coin.objects.get(symbol=symbol.upper())
        except Coin.DoesNotExist:
            logger.error(f"Coin {symbol} not found in database")
            return False

        # Calculate technical indicators
        df = calculate_technical_indicators(df)
        
        # Create a 12h shifted dataframe for price change calculation
        df_12h_ago = df.shift(1)  # For 12h candles, shift by 1 row for 12h change
        
        bulk_data = []
        
        for idx, row in df.iterrows():
            # Calculate 12h price change
            old_price = df_12h_ago.loc[idx, 'close_price'] if idx > 0 else None
            current_price = float(row['close_price'])
            
            if old_price and float(old_price) > 0:
                price_change = ((current_price - float(old_price)) / float(old_price) * 100)
            else:
                price_change = 0
            
            market_data = MarketData(
                symbol=coin,
                open_time=row['open_time'],
                close_time=row['close_time'],
                open_price=float(row['open_price']),
                high_price=float(row['high_price']),
                low_price=float(row['low_price']),
                close_price=current_price,
                volume=float(row['volume']),
                quote_volume=float(row['quote_volume']),
                num_trades=int(row['num_trades']),
                taker_buy_base_volume=float(row['taker_buy_base']),
                taker_buy_quote_volume=float(row['taker_buy_quote']),
                price_change_percent_24h=round(price_change, 2),
                
                # Add technical indicators
                rsi=round(float(row['RSI']), 2) if not pd.isna(row['RSI']) else None,
                macd=float(row['MACD']) if not pd.isna(row['MACD']) else None,
                macd_signal=float(row['MACD_Signal']) if not pd.isna(row['MACD_Signal']) else None,
                macd_hist=float(row['MACD_Hist']) if not pd.isna(row['MACD_Hist']) else None,
                bb_upper=float(row['BB_Upper']) if not pd.isna(row['BB_Upper']) else None,
                bb_middle=float(row['BB_Middle']) if not pd.isna(row['BB_Middle']) else None,
                bb_lower=float(row['BB_Lower']) if not pd.isna(row['BB_Lower']) else None,
                atr=float(row['ATR']) if not pd.isna(row['ATR']) else None,
                williams_r=float(row['Williams_R']) if not pd.isna(row['Williams_R']) else None
            )
            bulk_data.append(market_data)
            
            # Bulk create in chunks of 50 (optimized for 12h data)
            if len(bulk_data) >= 50:
                with transaction.atomic():
                    MarketData.objects.bulk_create(
                        bulk_data,
                        batch_size=50,
                        ignore_conflicts=True
                    )
                logger.info(f"Saved {len(bulk_data)} records for {symbol}")
                bulk_data = []
        
        # Save remaining records
        if bulk_data:
            with transaction.atomic():
                MarketData.objects.bulk_create(
                    bulk_data,
                    batch_size=50,
                    ignore_conflicts=True
                )
            logger.info(f"Saved final {len(bulk_data)} records for {symbol}")
        
        total_records = MarketData.objects.filter(symbol=coin).count()
        logger.info(f"Total records for {symbol}: {total_records}")
        return True
        
    except Exception as e:
        logger.error(f"Error in process_and_save_data for {symbol}: {str(e)}")
        return False

if __name__ == '__main__':
    # List of coins to process (excluding stablecoins)
    coins = ['BTC', 'ETH', 'SOL', 'XRP', 'LTC']
    
    # Calculate date range for 1.25 years of data
    end_time = timezone.now()
    start_time = end_time - timedelta(days=456)  # 365 + 91 days (1.25 years)
    
    logger.info(f"Processing 12h historical data from {start_time} to {end_time}")
    logger.info(f"Expected candles per coin: ~912 (456 days * 2 per day)")
    
    total_processed = 0
    successful_coins = []
    failed_coins = []
    
    for symbol in coins:
        try:
            logger.info(f"Processing {symbol}...")
            
            # 1. Fetch historical data
            df = fetch_historical_data_from_binance(symbol, start_time, end_time)
            if df is None:
                logger.error(f"Failed to fetch data for {symbol}, skipping...")
                failed_coins.append(symbol)
                continue
                
            # 2. Process and save data
            success = process_and_save_data(symbol, df)
            if success:
                logger.info(f"Successfully processed {symbol} with {len(df)} records")
                successful_coins.append(symbol)
                total_processed += len(df)
            else:
                logger.error(f"Failed to process {symbol}")
                failed_coins.append(symbol)
                
        except Exception as e:
            logger.error(f"Error processing {symbol}: {str(e)}")
            failed_coins.append(symbol)
            continue
    
    logger.info("=" * 50)
    logger.info("PROCESSING SUMMARY:")
    logger.info(f"Total records processed: {total_processed}")
    logger.info(f"Successful coins: {successful_coins}")
    logger.info(f"Failed coins: {failed_coins}")
    logger.info("=" * 50)
