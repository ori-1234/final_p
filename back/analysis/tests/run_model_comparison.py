# import os
# import sys
# import django
# import pandas as pd
# import matplotlib.pyplot as plt
# from datetime import datetime

# # Add the project root directory to Python path
# project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sys.path.append(project_root)

# # Set up Django environment
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
# django.setup()

# from analysis.ml_models.model_comparison import ModelComparison  # Updated import path

# def run_comparison_analysis(symbol_id=1, days=30, forecast_days=7):
#     """
#     Run comprehensive model comparison analysis.
    
#     Args:
#         symbol_id (int): ID of the cryptocurrency to analyze
#         days (int): Number of days of historical data to use
#         forecast_days (int): Number of days to forecast
#     """
#     try:
#         print(f"\n=== Starting Model Comparison Analysis ===")
#         print(f"Symbol ID: {symbol_id}")
#         print(f"Historical Days: {days}")
#         print(f"Forecast Days: {forecast_days}")
#         print("=" * 50)

#         # Initialize comparison
#         comparison = ModelComparison(symbol_id=symbol_id, days=days)
        
#         # Prepare data splits
#         print("\nPreparing data splits...")
#         comparison.prepare_train_test_split(test_size=0.2)
        
#         # Train all models
#         print("\nTraining models...")
#         comparison.train_all_models()
        
#         # Make predictions
#         print(f"\nMaking {forecast_days}-day predictions...")
#         comparison.make_predictions(forecast_steps=forecast_days)
        
#         # Evaluate models
#         print("\nEvaluating model performance...")
#         comparison.evaluate_models()
        
#         # Plot comparison
#         print("\nGenerating comparison plots...")
#         comparison.plot_comparison()
        
#         # Print metrics
#         print("\nModel Performance Metrics:")
#         comparison.print_metrics()
        
#         # Save results
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#         results_dir = "analysis_results"
        
#         # Create results directory if it doesn't exist
#         if not os.path.exists(results_dir):
#             os.makedirs(results_dir)
            
#         # Save metrics to CSV
#         metrics_file = f"{results_dir}/model_metrics_{timestamp}.csv"
#         metrics_df = pd.DataFrame(comparison.metrics)
#         metrics_df.to_csv(metrics_file)
#         print(f"\nMetrics saved to: {metrics_file}")
        
#         print("\nAnalysis complete!")
#         return comparison
        
#     except Exception as e:
#         print(f"\nError during analysis: {str(e)}")
#         import traceback
#         traceback.print_exc()
#         return None

# def main():
#     """
#     Main function to run model comparison analysis with different configurations.
#     """
#     try:
#         # Configuration parameters
#         symbols = [1]  # Add more symbol IDs as needed
#         historical_days = [30]  # Add more time periods as needed
#         forecast_days = 7
        
#         print("\n=== Cryptocurrency Price Prediction Model Comparison ===")
#         print(f"Running analysis for {len(symbols)} symbols")
#         print(f"Time periods: {historical_days} days")
#         print(f"Forecast horizon: {forecast_days} days")
#         print("=" * 50)
        
#         results = {}
        
#         # Run analysis for each symbol and time period
#         for symbol_id in symbols:
#             results[symbol_id] = {}
#             for days in historical_days:
#                 print(f"\nAnalyzing Symbol {symbol_id} with {days} days of historical data")
#                 results[symbol_id][days] = run_comparison_analysis(
#                     symbol_id=symbol_id,
#                     days=days,
#                     forecast_days=forecast_days
#                 )
        
#         print("\n=== Analysis Summary ===")
#         for symbol_id in results:
#             for days in results[symbol_id]:
#                 if results[symbol_id][days] is not None:
#                     print(f"\nSymbol {symbol_id} - {days} days:")
#                     print("-" * 30)
#                     # Add any summary statistics you want to display
        
#         print("\nAll analyses completed successfully!")
        
#     except Exception as e:
#         print(f"\nError in main execution: {str(e)}")
#         import traceback
#         traceback.print_exc()

# if __name__ == "__main__":
#     main()