import json
import asyncio
import websockets
import logging
from threading import Thread
from channels.generic.websocket import AsyncWebsocketConsumer
from datetime import datetime
from redis_cache.cache_utils.market import MarketDataCache

logger = logging.getLogger(__name__)

class BinanceWebSocketConsumer(AsyncWebsocketConsumer):
    BINANCE_WS_URL = "wss://fstream.binance.com/stream"
    COINS = ["BTC", "ETH", "SOL", "XRP", "LTC"]
    TRADING_PAIRS = [f"{coin.lower()}usdt" for coin in COINS]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize market updates dictionary for all pairs using base symbol (without usdt)
        self.market_updates = {coin.lower(): {
            "symbol": coin.upper(),  # Store uppercase symbol without usdt
            "current_price": 0.0,
            "high": 0.0,
            "low": 0.0,
            "volume": 0.0,
            "price_change_percent_24h": 0.0,
            "updated_at": datetime.now().isoformat()
        } for coin in self.COINS}

    async def connect_to_binance(self):
        """Connect to Binance WebSocket and process messages."""
        # Create streams for all trading pairs
        streams = [f"{pair}@ticker" for pair in self.TRADING_PAIRS]
        streams_url = f"{self.BINANCE_WS_URL}?streams={'/'.join(streams)}"
        
        logger.info(f"Connecting to Binance: {streams_url}")
        
        while True:
            try:
                async with websockets.connect(streams_url) as ws:
                    logger.info("Connected to Binance WebSocket")
                    
                    while True:
                        try:
                            message = await ws.recv()
                            await self.process_message(message)
                        except websockets.ConnectionClosed:
                            logger.warning("Binance connection closed")
                            break
                        except Exception as e:
                            logger.error(f"Error: {e}")
                            continue
            except Exception as e:
                logger.error(f"Connection error: {e}")
                await asyncio.sleep(5)

    async def process_message(self, message):
        """Process WebSocket message and update cache for all coins."""
        try:
            data = json.loads(message)
            stream_data = data.get('data', {})

            if stream_data:
                # Extract base symbol (remove 'usdt')
                full_symbol = stream_data["s"].lower()
                base_symbol = full_symbol.replace('usdt', '')
                
                # Update data for this symbol
                if base_symbol in self.market_updates:  # Only update if it's one of our tracked coins
                    self.market_updates[base_symbol].update({
                        "symbol": base_symbol.upper(),  # Store uppercase without usdt
                        "current_price": float(stream_data["c"]),
                        "high": float(stream_data["h"]),
                        "low": float(stream_data["l"]),
                        "volume": float(stream_data["v"]),
                        "price_change_percent_24h": float(stream_data["P"]),
                        "updated_at": datetime.now().isoformat()
                    }) 
                    
                    # Save ONLY the base symbol data
                    MarketDataCache.set_market_data(base_symbol, self.market_updates[base_symbol])
                    

        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
        except Exception as e:
            logger.error(f"Processing error: {e}")


    def run(self):
        """Run the WebSocket connection as an asyncio event loop."""
        asyncio.run(self.connect_to_binance())

    def start(self):
        """Start WebSocket in a separate thread when Django starts."""
        thread = Thread(target=self.run, daemon=True)
        thread.start()
        logger.info("Binance WebSocket service started")

    async def connect(self):
        """Handle WebSocket connection from clients."""
        await self.accept()
        logger.info("Client WebSocket connection accepted")

    async def disconnect(self, close_code):
        """Handle client disconnection."""
        logger.info(f"Client disconnected with code: {close_code}")



 