# import os
# import sys
# import django

# # Add the project root directory to Python path
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# # Set up Django environment
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
# django.setup()

# from ml_models.statistical_analysis import StatisticalAnalyzer

# def main():
#     try:
#         # Initialize analyzer for Bitcoin (symbol_id=1) with 30 days of data
#         analyzer = StatisticalAnalyzer(symbol_id=1, days=30)

#         # Analyze all features
#         analyzer.analyze_all_features()

#         # Print detailed statistics for each feature
#         analyzer.print_feature_statistics()

#         # Generate and save comprehensive report
#         report = analyzer.generate_feature_report(save_path='feature_statistics.csv')
        
#         print("\nAnalysis complete!")
        
#     except Exception as e:
#         print(f"An error occurred: {str(e)}")
#         import traceback
#         traceback.print_exc()

# if __name__ == "__main__":
#     main()