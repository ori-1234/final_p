from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from .models import Coin, MarketData
from redis_cache.cache_utils.market import MarketDataCache as MarketCache
import json
import logging
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
# views.py
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

logger = logging.getLogger(__name__)


    
@api_view(['GET'])
@permission_classes([AllowAny])
def market_overview(request):
    try:
        response_data = []
        
        # Get all coins from the Coin model (exclude USD and USDC)
        coins = Coin.objects.exclude(symbol__in=['USD', 'USDC'])
        
        for coin in coins:
            # Get cache data for this symbol
            cache_data = MarketCache.get_market_data(coin.symbol.lower()) or {}
            
            # Format numbers properly
            current_price = float(cache_data.get('current_price', 0))
            volume = float(cache_data.get('volume', 0))
            price_change = float(cache_data.get('price_change_percent_24h', 0))
            
            # Create coin data with the exact structure needed by the Grid component
            coin_data = {
                "id": coin.symbol,
                "name": coin.name,
                "symbol": coin.symbol,
                "image": coin.logo or "",
                "desc": coin.description or "",
                "current_price": current_price,
                "total_volume": volume,
                "price_change_percentage_24h": price_change,
                "market_cap": volume * current_price,  # Calculate market cap if needed
                "last_updated": cache_data.get('updated_at', ""),
            }
            
            # Add to response array only if we have valid price data
            if current_price > 0:
                response_data.append(coin_data)
        
        logger.info(f"Sending market data: {json.dumps(response_data)}")
        
        # Return JSON response with proper numeric values
        return HttpResponse(
            json.dumps(response_data, default=str),  # Use default=str for datetime objects
            content_type='application/json'
        )
        
    except Exception as e:
        logger.error(f"Error in market_overview: {str(e)}")
        return HttpResponse(
            json.dumps({"error": "Failed to fetch market data"}),
            content_type='application/json',
            status=500
        )
    



@api_view(['GET'])
@permission_classes([AllowAny])
def coin_details(request, pk=None):
    """
    Returns daily market data for a specific coin over multiple timeframes.
    """
    try:
        if not pk:
            return Response(
                {"error": "Coin symbol is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        symbol = pk.upper()
        
        # 1) First verify coin exists
        coin = get_object_or_404(Coin, symbol=symbol)
        
        # 2) Try to get complete data from cache
        cached_data = MarketCache.get_chart_data(symbol)
        cached_volume_data = MarketCache.get_volume_data(symbol)
        cache_data = MarketCache.get_market_data(coin.symbol.lower()) or {}

        current_price = float(cache_data.get('current_price', 0))
        volume = float(cache_data.get('volume', 0))
        
        # 3) Get current market data
        market_data = MarketCache.get_market_data(coin.symbol.lower()) or {}
        
        # 4) Prepare response data
        response_data = {
            "id": coin.id,
            "name": coin.name,
            "symbol": coin.symbol,
            "logo": coin.logo or "",
            "description": coin.description or "",
            "current_price": float(market_data.get('current_price', 0)),
            "price_change_percent_24h": float(market_data.get('price_change_percent_24h', 0)),
            "high_24h": float(market_data.get('high', 0)),
            "low_24h": float(market_data.get('low', 0)),
            "volume": float(market_data.get('volume', 0)),
            "last_updated": market_data.get('updated_at', ""),
            "market_cap": volume * current_price,  # Calculate market cap if needed
        }

        # 5) If we have cached chart data, use it
        if cached_data and cached_data.get('chart_data'):
            response_data['chart_data'] = cached_data['chart_data']
        else:
            # If no cached data, generate it now synchronously
            logger.info(f"No cached chart data for {symbol}, generating now...")
            from .tasks import update_coin_details_cache
            # Schedule an async update instead of blocking
            update_coin_details_cache.delay(symbol)
            # Return empty chart data for now
            response_data['chart_data'] = {
                str(days): [] for days in [7, 30, 60, 90, 120, 365]
            }

        # 6) Add volume data if available
        if cached_volume_data and cached_volume_data.get('volume_data'):
            response_data['volume_data'] = cached_volume_data['volume_data']
        else:
            # If no cached volume data, generate it asynchronously
            logger.info(f"No cached volume data for {symbol}, generating now...")
            from .tasks import update_coin_volume_cache
            # Schedule an async update instead of blocking
            update_coin_volume_cache.delay(symbol)
            # Return empty volume data for now
            response_data['volume_data'] = {
                str(days): [] for days in [7, 30, 60, 90, 120, 365]
            }

        return Response(response_data)

    except Exception as e:
        logger.error(f"Error in coin_details for {pk}: {str(e)}")
        return Response(
            {"error": f"Failed to fetch coin details: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        


@api_view(['GET'])
@permission_classes([AllowAny])
def compare_coins(request):
    """
    Returns cached chart data for all coins (expected: all 5 coins).
    The JSON response follows the structure:
    
        market_data[symbol] = {
            "id": coin.id,
            "name": coin.name,
            "symbol": symbol,
            "logo": coin.logo or "",
            "current_price": float(current_data.get('current_price', 0)),
            "price_change_percent_24h": float(current_data.get('price_change_percent_24h', 0)),
            "high_24h": float(current_data.get('high', 0)),
            "low_24h": float(current_data.get('low', 0)),
            "volume": float(current_data.get('volume', 0)),
            "last_updated": current_data.get('updated_at', ""),
            "chart_data": chart_data.get('chart_data', {}) if chart_data else {},
        }
    """
    try:
        coins = Coin.objects.exclude(symbol__in=['USD', 'USDC'])  # Exclude USD and USDC
        market_data = {}

        for coin in coins:
            symbol = coin.symbol.upper()
            # Retrieve cached chart data for this coin
            cached_data = MarketCache.get_chart_data(symbol)
            cached_volume_data = MarketCache.get_volume_data(symbol)

            # Retrieve current market data for this coin
            current_data = MarketCache.get_market_data(symbol.lower()) or {}

            current_price = float(current_data.get('current_price', 0))
            volume = float(current_data.get('volume', 0))

            coin_data = {
                "id": coin.id,
                "name": coin.name,
                "symbol": symbol,
                "logo": coin.logo or "",
                "description": coin.description or "",
                "current_price": float(current_data.get('current_price', 0)),
                "price_change_percent_24h": float(current_data.get('price_change_percent_24h', 0)),
                "high_24h": float(current_data.get('high', 0)),
                "low_24h": float(current_data.get('low', 0)),
                "volume": float(current_data.get('volume', 0)),
                "last_updated": current_data.get('updated_at', ""),
                "market_cap": volume * current_price,  # Calculate market cap if needed
            }
            
            # Use cached chart data if available; otherwise, generate it synchronously.
            if cached_data and cached_data.get('chart_data'):
                coin_data["chart_data"] = cached_data.get('chart_data')
            else:
                logger.info(f"No cached chart data for {symbol}, generating now...")
                from .tasks import update_coin_details_cache
                cache_data = update_coin_details_cache(symbol)
                if cache_data and cache_data.get('chart_data'):
                    coin_data["chart_data"] = cache_data.get('chart_data')
                else:
                    # Return empty chart_data for the known timeframes
                    coin_data["chart_data"] = {str(d): [] for d in [7, 30, 60, 90, 120, 365]}
            
            # Use cached volume data if available; otherwise, generate it synchronously.
            if cached_volume_data and cached_volume_data.get('volume_data'):
                coin_data["volume_data"] = cached_volume_data.get('volume_data')
            else:
                logger.info(f"No cached volume data for {symbol}, generating now...")
                from .tasks import update_coin_volume_cache
                volume_cache_data = update_coin_volume_cache(symbol)
                if volume_cache_data and volume_cache_data.get('volume_data'):
                    coin_data["volume_data"] = volume_cache_data.get('volume_data')
                else:
                    # Return empty volume_data for the known timeframes
                    coin_data["volume_data"] = {str(d): [] for d in [7, 30, 60, 90, 120, 365]}

            market_data[symbol] = coin_data

        return Response({"data": market_data})
    
    except Exception as e:
        logger.error(f"Error in compare_coins view: {str(e)}")
        return Response(
            {"error": f"Failed to fetch compare data: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

