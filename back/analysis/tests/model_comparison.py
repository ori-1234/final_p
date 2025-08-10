# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# from datetime import datetime, timedelta
# from django.utils import timezone
# from analytics.models import MarketData
# from ml_models.arima import ArimaAnalyzer
# from ml_models.prophet import ProphetAnalyzer
# from ml_models.random_forest import RandomForestAnalyzer
# from ml_models.sarimax import SARIMAXAnalyzer
# from ml_models.xgboost import XGBoostAnalyzer
# from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# class ModelComparison:
#     def __init__(self, symbol_id, days=30):
#         self.symbol_id = symbol_id
#         self.days = days
#         self.data = self._load_market_data()
#         self.models = {}
#         self.predictions = {}
#         self.metrics = {}
        
#     def _load_market_data(self):
#         end_date = timezone.now()
#         start_date = end_date - timedelta(days=self.days)
        
#         market_data = MarketData.objects.filter(
#             symbol_id=self.symbol_id,
#             close_time__range=(start_date, end_date)
#         ).order_by('close_time')
        
#         df = pd.DataFrame(list(market_data.values()))
        
#         # Convert numeric columns to float
#         numeric_columns = ['open_price', 'high_price', 'low_price', 'close_price', 
#                          'volume', 'quote_volume', 'num_trades', 
#                          'taker_buy_base_volume', 'taker_buy_quote_volume']
#         for col in numeric_columns:
#             if col in df.columns:
#                 df[col] = pd.to_numeric(df[col], errors='coerce')
        
#         return df
    
#     def prepare_train_test_split(self, test_size=0.2):
#         """
#         Prepare train-test splits for all models.
#         """
#         split_idx = int(len(self.data) * (1 - test_size))
#         self.train_data = self.data[:split_idx]
#         self.test_data = self.data[split_idx:]
        
#         # Create DatetimeIndex with proper frequency
#         train_index = pd.DatetimeIndex(self.train_data['close_time']).floor('min')
#         test_index = pd.DatetimeIndex(self.test_data['close_time']).floor('min')
        
#         # Create time series with proper index
#         self.train_ts = pd.Series(
#             self.train_data['close_price'].values,
#             index=train_index
#         )
#         self.test_ts = pd.Series(
#             self.test_data['close_price'].values,
#             index=test_index
#         )
        
#         # Prepare Prophet data
#         self.train_prophet = pd.DataFrame({
#             'ds': self.train_data['close_time'],
#             'y': self.train_data['close_price']
#         })
#         self.test_prophet = pd.DataFrame({
#             'ds': self.test_data['close_time'],
#             'y': self.test_data['close_price']
#         })
    
#     def train_all_models(self):
#         # ARIMA
#         print("Training ARIMA model...")
#         self.models['ARIMA'] = ArimaAnalyzer(self.train_ts)
#         self.models['ARIMA'].fit()
        
#         # SARIMAX
#         print("Training SARIMAX model...")
#         self.models['SARIMAX'] = SARIMAXAnalyzer(self.train_ts)
#         self.models['SARIMAX'].fit()
        
#         # Prophet
#         print("Training Prophet model...")
#         self.models['Prophet'] = ProphetAnalyzer()
#         self.models['Prophet'].fit(self.train_prophet)
        
#         # XGBoost
#         print("Training XGBoost model...")
#         self.models['XGBoost'] = XGBoostAnalyzer()
#         self.models['XGBoost'].train_model(self.train_data)
        
#         # Random Forest
#         print("Training Random Forest model...")
#         self.models['RandomForest'] = RandomForestAnalyzer()
#         rf_features = self.train_data[[
#             'open_price', 'high_price', 'low_price', 'volume',
#             'quote_volume', 'num_trades'
#         ]].astype(float)
#         self.models['RandomForest'].fit(
#             data=rf_features,
#             target=self.train_data['close_price'].astype(float)
#         )
    
#     def make_predictions(self, forecast_steps=7):
#         for model_name, model in self.models.items():
#             print(f"Making predictions with {model_name}...")
#             try:
#                 if model_name in ['ARIMA', 'SARIMAX']:
#                     self.predictions[model_name] = model.predict(steps=forecast_steps)
#                 elif model_name == 'Prophet':
#                     prophet_forecast = model.predict(steps=forecast_steps)
#                     self.predictions[model_name] = prophet_forecast['yhat'].values
#                 elif model_name == 'XGBoost':
#                     self.predictions[model_name] = model.predict(self.test_data, steps=forecast_steps)
#                 elif model_name == 'RandomForest':
#                     rf_features = self.test_data[[
#                         'open_price', 'high_price', 'low_price', 'volume',
#                         'quote_volume', 'num_trades'
#                     ]].astype(float)
#                     self.predictions[model_name] = model.predict(rf_features)[:forecast_steps]
#             except Exception as e:
#                 print(f"Error predicting with {model_name}: {str(e)}")
    
#     def evaluate_models(self):
#         actual_values = self.test_data['close_price'].values[:len(next(iter(self.predictions.values())))]
        
#         for model_name, predictions in self.predictions.items():
#             try:
#                 mse = mean_squared_error(actual_values, predictions)
#                 rmse = np.sqrt(mse)
#                 mae = mean_absolute_error(actual_values, predictions)
#                 r2 = r2_score(actual_values, predictions)
                
#                 self.metrics[model_name] = {
#                     'MSE': mse,
#                     'RMSE': rmse,
#                     'MAE': mae,
#                     'R2': r2
#                 }
#             except Exception as e:
#                 print(f"Error evaluating {model_name}: {str(e)}")
    
#     def plot_comparison(self):
#         """
#         Create comprehensive comparison plots with improved visualization
#         """
#         plt.style.use('seaborn')
#         fig = plt.figure(figsize=(15, 12))
        
#         # Plot 1: Price Predictions
#         ax1 = plt.subplot(2, 1, 1)
        
#         # Plot actual values
#         actual = self.test_data['close_price'].values[:len(next(iter(self.predictions.values())))]
#         ax1.plot(actual, 'k-', label='Actual', linewidth=2)
        
#         # Plot predictions for each model with different styles
#         colors = ['#FF9999', '#66B2FF', '#99FF99', '#FFCC99', '#FF99CC']  # Added color for Prophet
#         linestyles = ['-', '--', '-.', ':', '--']  # Added style for Prophet
        
#         for (model_name, predictions), color, ls in zip(self.predictions.items(), colors, linestyles):
#             ax1.plot(predictions, color=color, linestyle=ls, label=f'{model_name}', linewidth=2)
        
#         ax1.set_title('Model Predictions Comparison', fontsize=12, pad=20)
#         ax1.set_xlabel('Time Steps')
#         ax1.set_ylabel('Price')
#         ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
#         ax1.grid(True, alpha=0.3)
        
#         # Plot 2: Performance Metrics
#         ax2 = plt.subplot(2, 1, 2)
        
#         metrics_df = pd.DataFrame(self.metrics).round(4)
#         bar_width = 0.15  # Reduced width to accommodate more models
#         r = np.arange(len(metrics_df.index))
        
#         for idx, (model_name, metrics) in enumerate(self.metrics.items()):
#             ax2.bar(r + idx * bar_width, 
#                    metrics.values(), 
#                    bar_width, 
#                    label=model_name,
#                    color=colors[idx],
#                    alpha=0.7)
        
#         ax2.set_xlabel('Metrics')
#         ax2.set_ylabel('Value')
#         ax2.set_title('Model Performance Metrics Comparison', fontsize=12, pad=20)
#         ax2.set_xticks(r + bar_width * (len(self.metrics) - 1) / 2)
#         ax2.set_xticklabels(metrics_df.index)
#         ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
#         ax2.grid(True, alpha=0.3)
        
#         plt.tight_layout()
#         plt.show()
    
#     def print_metrics(self):
#         if not self.metrics:
#             print("No metrics available. Run evaluate_models() first.")
#             return
            
#         print("\nModel Performance Metrics:")
#         print("-" * 50)
        
#         metrics_df = pd.DataFrame(self.metrics).round(4)
#         print(metrics_df)
        
#         # Find best model for each metric
#         best_models = {}
#         for metric in metrics_df.index:
#             if metric in ['MSE', 'RMSE', 'MAE']:
#                 best_models[metric] = metrics_df.loc[metric].idxmin()
#             else:  # R2
#                 best_models[metric] = metrics_df.loc[metric].idxmax()
        
#         print("\nBest Models:")
#         for metric, model in best_models.items():
#             value = metrics_df.loc[metric, model]
#             print(f"{metric}: {model} ({value:.4f})")