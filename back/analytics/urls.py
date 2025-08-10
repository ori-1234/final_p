from django.urls import path
from .views import market_overview, coin_details, compare_coins

urlpatterns = [
    path('market_overview/', market_overview, name='market-overview'),
    path('coin_details/<str:pk>/', coin_details, name='coin-details'),
    path('compare_coins/', compare_coins, name='compare-coins'),
] 