from django.db import models
from django.utils import timezone

class TechnicalFeatures(models.Model):
    symbol = models.ForeignKey('analytics.Coin', on_delete=models.CASCADE, related_name='technical_features')
    timestamp = models.ForeignKey('analytics.MarketData', on_delete=models.CASCADE, related_name='technical_features')
    record_timestamp = models.DateTimeField(null=True) # Add this line
    
    prev_atr_lag9 = models.FloatField(null=True)
    prev_macd_signal_lag4 = models.FloatField(null=True)
    prev_rsi_ma5 = models.FloatField(null=True)
    prev_bb_lower_lag10 = models.FloatField(null=True)
    prev_quote_volume_ma8 = models.FloatField(null=True)
    prev_macd_hist_std8_ma = models.FloatField(null=True)
    prev_williams_r_ma7 = models.FloatField(null=True)
    volume_prev_ma10 = models.FloatField(null=True)
    prev_quote_volume_ma7 = models.FloatField(null=True)
    prev_close_ma5 = models.FloatField(null=True)
    prev_macd_hist_std7_ma = models.FloatField(null=True)
    prev_taker_buy_base_volume_std7_ma = models.FloatField(null=True)
    prev_rsi_std2_ma = models.FloatField(null=True)
    prev_taker_buy_quote_volume_lag10 = models.FloatField(null=True)

    # Price change features
    change_pct = models.FloatField(null=True, db_column='2_periods_back_back_change_pct')
    change_pct_lag1 = models.FloatField(null=True, db_column='2_periods_back_back_change_pct_lag1')
    change_pct_lag4 = models.FloatField(null=True, db_column='2_periods_back_back_change_pct_lag4')
    change_pct_lag8 = models.FloatField(null=True, db_column='2_periods_back_back_change_pct_lag8')

    class Meta:
        indexes = [
            models.Index(fields=["symbol", "timestamp"]),
        ]


class SentimentFeatures(models.Model):
    symbol = models.ForeignKey('analytics.Coin', on_delete=models.CASCADE, related_name='sentiment_features')
    timestamp = models.ForeignKey('analytics.MarketData', on_delete=models.CASCADE, related_name='sentiment_features')
    record_timestamp = models.DateTimeField(null=True)

    prev_num_articles_ma1_10 = models.FloatField(null=True)
    prev_extremely_positive_count_ma1_5 = models.FloatField(null=True)
    prev_avg_sentiment_std1_6_ma = models.FloatField(null=True)
    prev_extremely_positive_count_ma1_4 = models.FloatField(null=True)
    prev_extremely_negative_count_lag5 = models.FloatField(null=True)
    avg_sentiment_news_prev_std5_ma = models.FloatField(null=True)
    prev_avg_sentiment_lag4 = models.FloatField(null=True)
    prev_min_sentiment_lag10 = models.FloatField(null=True)
    prev_std_sentiment_lag1 = models.FloatField(null=True)
    prev_min_sentiment_lag1 = models.FloatField(null=True)
    prev_std_sentiment_lag3 = models.FloatField(null=True)
    prev_median_sentiment_lag8 = models.FloatField(null=True)
    prev_extremely_negative_count_std1_9_ma = models.FloatField(null=True)

    class Meta:
        indexes = [
            models.Index(fields=["symbol", "timestamp"]),
        ]




class FullAnalysis(models.Model):
    symbol = models.ForeignKey("analytics.Coin", on_delete=models.CASCADE)

    # תאריך חצי יומי, למשל 2025-07-10 12:00
    timestamp = models.DateTimeField()

    # ניתוחים טקסטואליים
    sentiment_analysis_text = models.TextField(null=True, blank=True)
    technical_analysis_text = models.TextField(null=True, blank=True)
    strategy_analysis_text = models.TextField(null=True, blank=True)

    # קלסיפיקציה בינארית: 0 = ירד, 1 = יעלה
    classification = models.IntegerField(choices=[(0, 'Down'), (1, 'Up')], null=True)


    class Meta:
        indexes = [
            models.Index(fields=["symbol", "timestamp"]),
        ]
        unique_together = ("symbol", "timestamp")
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.symbol.symbol} | {self.half_day_key} | ↑" if self.classification == 1 else f"{self.symbol.symbol} | {self.half_day_key} | ↓"
