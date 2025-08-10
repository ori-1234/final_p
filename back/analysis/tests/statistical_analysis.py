# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# import seaborn as sns
# from scipy import stats
# from django.utils import timezone
# from datetime import timedelta
# from analytics.models import MarketData
# from decimal import Decimal

# class StatisticalAnalyzer:
#     """
#     A class for analyzing individual features of cryptocurrency market data.
#     """
    
#     def __init__(self, symbol_id=None, days=30):
#         self.symbol_id = symbol_id
#         self.days = days
#         self.data = None
#         self.feature_stats = {}
        
#         if symbol_id:
#             self.load_data()
    
#     def load_data(self, symbol_id=None, days=None):
#         if symbol_id:
#             self.symbol_id = symbol_id
#         if days:
#             self.days = days
            
#         end_date = timezone.now()
#         start_date = end_date - timedelta(days=self.days)
        
#         market_data = MarketData.objects.filter(
#             symbol_id=self.symbol_id,
#             close_time__range=(start_date, end_date)
#         ).order_by('close_time')
        
#         # Convert to DataFrame and convert Decimal to float
#         self.data = pd.DataFrame(list(market_data.values()))
        
#         # Convert Decimal columns to float
#         decimal_columns = [
#             'open_price', 'close_price', 'high_price', 'low_price',
#             'volume', 'quote_volume', 'taker_buy_base_volume', 'taker_buy_quote_volume',
#             'rsi', 'macd', 'macd_signal', 'macd_hist', 'bb_upper', 'bb_middle', 'bb_lower'
#         ]
        
#         for col in decimal_columns:
#             if col in self.data.columns:
#                 self.data[col] = self.data[col].astype(float)
        
#         return self.data

#     def analyze_price_features(self):
#         """Analyze price-related features"""
#         price_features = ['open_price', 'close_price', 'high_price', 'low_price']
#         stats = {}
        
#         for feature in price_features:
#             if feature in self.data.columns:
#                 series = pd.to_numeric(self.data[feature], errors='coerce').dropna()
#                 stats[feature] = {
#                     'mean': float(series.mean()),
#                     'variance': float(series.var()),
#                     'skew': float(series.skew()),
#                     'median': float(series.median()),
#                     'min': float(series.min()),
#                     'max': float(series.max())
#                 }
        
#         return stats

#     def analyze_volume_features(self):
#         """Analyze volume-related features"""
#         volume_features = ['volume', 'quote_volume', 'taker_buy_base_volume', 'taker_buy_quote_volume']
#         stats = {}
        
#         for feature in volume_features:
#             if feature in self.data.columns:
#                 series = pd.to_numeric(self.data[feature], errors='coerce').dropna()
#                 stats[feature] = {
#                     'mean': float(series.mean()),
#                     'variance': float(series.var()),
#                     'skew': float(series.skew()),
#                     'median': float(series.median()),
#                     'min': float(series.min()),
#                     'max': float(series.max())
#                 }
        
#         return stats

#     def analyze_technical_indicators(self):
#         """Analyze technical indicators"""
#         technical_features = ['rsi', 'macd', 'macd_signal', 'macd_hist', 'bb_upper', 'bb_middle', 'bb_lower']
#         stats = {}
        
#         for feature in technical_features:
#             if feature in self.data.columns:
#                 series = pd.to_numeric(self.data[feature], errors='coerce').dropna()
#                 stats[feature] = {
#                     'mean': float(series.mean()),
#                     'variance': float(series.var()),
#                     'skew': float(series.skew()),
#                     'median': float(series.median()),
#                     'min': float(series.min()),
#                     'max': float(series.max())
#                 }
        
#         return stats

#     def analyze_all_features(self):
#         """Analyze all features and store results"""
#         self.feature_stats['price_features'] = self.analyze_price_features()
#         self.feature_stats['volume_features'] = self.analyze_volume_features()
#         self.feature_stats['technical_indicators'] = self.analyze_technical_indicators()
#         return self.feature_stats

#     def print_feature_statistics(self):
#         """Print statistics for each feature category"""
#         if not self.feature_stats:
#             self.analyze_all_features()

#         print("\n=== Feature Statistics Analysis ===")
#         print(f"Symbol ID: {self.symbol_id}")
#         print(f"Period: {self.days} days")
#         print("=" * 50)

#         categories = {
#             'Price Features': 'price_features',
#             'Volume Features': 'volume_features',
#             'Technical Indicators': 'technical_indicators'
#         }

#         for category_name, category_key in categories.items():
#             print(f"\n{category_name}")
#             print("-" * 50)
            
#             if category_key in self.feature_stats:
#                 for feature, stats in self.feature_stats[category_key].items():
#                     print(f"\n{feature}:")
#                     print(f"  Mean:     {stats['mean']:,.4f}")
#                     print(f"  Variance: {stats['variance']:,.4f}")
#                     print(f"  Skew:     {stats['skew']:,.4f}")
#                     print(f"  Median:   {stats['median']:,.4f}")
#                     print(f"  Min:      {stats['min']:,.4f}")
#                     print(f"  Max:      {stats['max']:,.4f}")

#     def generate_feature_report(self, save_path=None):
#         """Generate a comprehensive report for all features"""
#         if not self.feature_stats:
#             self.analyze_all_features()

#         # Prepare data for DataFrame
#         report_data = []
#         for category, features in self.feature_stats.items():
#             for feature, stats in features.items():
#                 row = {
#                     'category': category,
#                     'feature': feature,
#                     **stats
#                 }
#                 report_data.append(row)

#         # Create DataFrame
#         report_df = pd.DataFrame(report_data)
        
#         # Reorder columns
#         columns = ['category', 'feature', 'mean', 'median', 'variance', 'skew', 'min', 'max']
#         report_df = report_df[columns]

#         if save_path:
#             report_df.to_csv(save_path, index=False)
#             print(f"\nReport saved to: {save_path}")

#         return report_df