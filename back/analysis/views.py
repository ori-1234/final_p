# back/analysis/views.py
import os
import sys
import joblib
import pandas as pd
import numpy as np
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import logging
from time import sleep

# Import models and cache utility
from redis_cache.cache_utils.analysis import AnalysisDataCache
from .models import TechnicalFeatures, SentimentFeatures
from analytics.models import Coin, MarketData, DailySentimentData
from .tasks import update_all_technical_features_for_symbol, update_all_sentiment_features_for_symbol
from celery import group
from django.core.exceptions import ObjectDoesNotExist
# --- ML Model Loading ---
MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ML_model')
MODEL_PATH = os.path.join(MODEL_DIR, 'final_xgb_model.pkl')
SCALER_PATH = os.path.join(MODEL_DIR, 'scaler_xgb_model.pkl')
STRATEGY_WORKFLOW_URL = os.environ.get('N8N_STRATEGY_WORKFLOW_URL')

# Lazy load to avoid crashing server startup if files missing; no mock fallback
model = None
scaler = None
logger = logging.getLogger(__name__)

def _ensure_model_loaded():
    global model, scaler
    if model is None or scaler is None:
        try:
            # Sanity: verify xgboost import before unpickle
            try:
                import xgboost  # noqa: F401
                logger.info(f"xgboost import OK (version={getattr(xgboost, '__version__', 'unknown')}).")
            except ImportError as ie:
                logger.error(
                    "Failed to import xgboost inside backend.\n"
                    f"Python: {sys.executable}\n"
                    f"sys.path (first 3): {sys.path[:3]} ...\n"
                    f"MODEL_DIR contents: {os.listdir(MODEL_DIR) if os.path.isdir(MODEL_DIR) else 'missing'}\n"
                    f"Error: {ie}"
                )
                raise

            logger.info(f"Loading model from {MODEL_PATH} and scaler from {SCALER_PATH}")
            model = joblib.load(MODEL_PATH)
            scaler = joblib.load(SCALER_PATH)
            logger.info("Model and scaler loaded successfully.")

            # Log model/scaler expected feature names if available
            try:
                model_feature_names = None
                if hasattr(model, 'feature_names_in_'):
                    model_feature_names = [str(x) for x in getattr(model, 'feature_names_in_')]
                elif hasattr(model, 'get_booster'):
                    try:
                        booster = model.get_booster()
                        model_feature_names = getattr(booster, 'feature_names', None)
                    except Exception:
                        model_feature_names = None
                elif hasattr(model, 'n_features_in_'):
                    model_feature_names = [f'f{i}' for i in range(int(getattr(model, 'n_features_in_', 0)))]

                logger.info(
                    "Model feature names (%s): %s",
                    len(model_feature_names) if model_feature_names is not None else 'unknown',
                    model_feature_names,
                )

                scaler_feature_names = getattr(scaler, 'feature_names_in_', None)
                logger.info(
                    "Scaler feature names (%s): %s",
                    len(scaler_feature_names) if scaler_feature_names is not None else 'unknown',
                    scaler_feature_names,
                )
            except Exception as e_info:
                logger.warning("Could not introspect model/scaler features: %s", e_info)
        except Exception as e:
            logger.exception(f"Model/scaler load failed: {e}")
            raise


@method_decorator(csrf_exempt, name='dispatch')
class N8NWebhookReceiver(APIView):
    """
    View 1: Receives analysis data from an n8n webhook and saves it to Redis cache.
    """
    permission_classes = []
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        try:
            analysis_data = request.data.get('analysis')
            if not isinstance(analysis_data, dict):
                return Response({'status': 'error', 'message': "Payload must contain a JSON object under the 'analysis' key."}, status=status.HTTP_400_BAD_REQUEST)
            
            ticker = analysis_data.get('ticker')
            if not ticker:
                return Response({'status': 'error', 'message': "The 'analysis' object must contain a 'ticker' symbol."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Ensure the ticker is always lowercase to maintain cache consistency
            ticker_lower = ticker.lower()
            
            AnalysisDataCache.set_analysis_data(ticker_lower, analysis_data)
            return Response({'status': 'success', 'message': f'Data for {ticker_lower} received and cached.'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class GetAnalysisResult(APIView):
    """
    View 2: Polling endpoint for the frontend to get cached analysis results.
    """
    permission_classes = []
    authentication_classes = []

    def get(self, request, symbol, *args, **kwargs):
        if not symbol:
            return Response({'status': 'error', 'message': 'A coin symbol must be provided in the URL.'}, status=status.HTTP_400_BAD_REQUEST)
        
        cached_data = AnalysisDataCache.get_analysis_data(symbol.upper())
        
        if cached_data:
            return Response({'status': 'success', 'data': cached_data}, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'no-data', 'message': f'No analysis data found for {symbol}.'}, status=status.HTTP_204_NO_CONTENT)




@method_decorator(csrf_exempt, name='dispatch')
class TriggerPredictionView(APIView):
    permission_classes = []
    authentication_classes = []

    # === פיצ'רים טכניים (כולל 4 ה-change_pct שעברו לטכני) ===
    TECH_FEATURES = [
        'prev_atr_lag9', 'prev_macd_signal_lag4', 'prev_rsi_ma5', 'prev_bb_lower_lag10',
        'prev_quote_volume_ma8', 'prev_macd_hist_std8_ma', 'prev_williams_r_ma7',
        'volume_prev_ma10', 'prev_quote_volume_ma7', 'prev_close_ma5',
        'prev_macd_hist_std7_ma', 'prev_taker_buy_base_volume_std7_ma',
        'prev_rsi_std2_ma', 'prev_taker_buy_quote_volume_lag10',
        '2_periods_back_back_change_pct', '2_periods_back_back_change_pct_lag1',
        '2_periods_back_back_change_pct_lag4', '2_periods_back_back_change_pct_lag8',
    ]

    # === פיצ'רי סנטימנט (ללא ה-change_pct) ===
    SENT_FEATURES = [
        'prev_num_articles_ma1_10', 'prev_extremely_positive_count_ma1_5',
        'prev_avg_sentiment_std1_6_ma', 'prev_extremely_positive_count_ma1_4',
        'prev_extremely_negative_count_lag5', 'avg_sentiment_news_prev_std5_ma',
        'prev_avg_sentiment_lag4', 'prev_min_sentiment_lag10', 'prev_std_sentiment_lag1',
        'prev_min_sentiment_lag1', 'prev_std_sentiment_lag3', 'prev_median_sentiment_lag8',
        'prev_extremely_negative_count_std1_9_ma',
    ]

    # === סדר הפיצ'רים המדויק שה-SCALER מצפה לו ===
    EXPECTED_FEATURES = [
        'prev_extremely_negative_count_std1_9_ma', 'prev_num_articles_ma1_10',
        'prev_extremely_positive_count_ma1_5', 'prev_atr_lag9',
        'prev_macd_signal_lag4', 'prev_rsi_ma5', 'prev_bb_lower_lag10',
        'prev_quote_volume_ma8', 'prev_macd_hist_std8_ma', 'prev_williams_r_ma7',
        'volume_prev_ma10', 'prev_quote_volume_ma7', 'prev_close_ma5',
        'prev_avg_sentiment_std1_6_ma', 'prev_macd_hist_std7_ma',
        'prev_extremely_positive_count_ma1_4',
        'prev_extremely_negative_count_lag5', 'prev_taker_buy_base_volume_std7_ma',
        'avg_sentiment_news_prev_std5_ma', '2_periods_back_back_change_pct',
        '2_periods_back_back_change_pct_lag1',
        '2_periods_back_back_change_pct_lag4', 'prev_avg_sentiment_lag4',
        'prev_min_sentiment_lag10', '2_periods_back_back_change_pct_lag8',
        'prev_std_sentiment_lag1', 'prev_min_sentiment_lag1',
        'prev_std_sentiment_lag3', 'prev_rsi_std2_ma',
        'prev_taker_buy_quote_volume_lag10', 'prev_median_sentiment_lag8'
    ]

    # === מיפוי משמות שהמודל מצפה להם לשמות שדות ב-DB ===
    MODEL_TO_DB_FIELD_MAP = {
        '2_periods_back_back_change_pct': 'change_pct',
        '2_periods_back_back_change_pct_lag1': 'change_pct_lag1',
        '2_periods_back_back_change_pct_lag4': 'change_pct_lag4',
        '2_periods_back_back_change_pct_lag8': 'change_pct_lag8',
    }
    
    EXTRA_COLS_TO_DROP = {'timestamp_id', 'record_timestamp', 'symbol_id', 'id'}

    def _extract_symbol(self, payload: dict) -> str | None:
        analysis = payload.get('analysis', payload)
        sym = (
            payload.get('ticker') or payload.get('symbol') or
            (analysis or {}).get('ticker') or (analysis or {}).get('symbol') or
            (((analysis or {}).get('technical_analysis', {})
               .get('analysis', {})
               .get('Quick_Stats', {})).get('Ticker'))
        )
        return sym.strip().upper() if isinstance(sym, str) and sym.strip() else None

    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """ניקוי/ולידציה והעמדה לפי הסדר שהמודל מצפה אליו."""
        # הסרת עמודות מיותרות
        drop_known = [c for c in df.columns if c in self.EXTRA_COLS_TO_DROP]
        df = df.drop(columns=drop_known, errors="ignore")

        # הסרת עמודות לא צפויות
        extras = [c for c in df.columns if c not in self.EXPECTED_FEATURES]
        if extras:
            df = df.drop(columns=extras, errors="ignore")

        # בדיקת חסרים
        missing = [c for c in self.EXPECTED_FEATURES if c not in df.columns]
        if missing:
            raise ValueError(f"Missing expected features: {missing}")

        # סידור עמודות
        df = df[self.EXPECTED_FEATURES].copy()

        # המרה למספרים + בדיקת NaN
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        if df.isna().any().any():
            bad_cols = df.columns[df.isna().any()].tolist()
            raise ValueError(f"NaN found in columns after numeric coercion: {bad_cols}")

        return df

    def predict_from_df(self, df_raw: pd.DataFrame) -> pd.DataFrame:
        _ensure_model_loaded() # Ensure model and scaler are loaded
        X = self.prepare_features(df_raw)

        # שמירה על DataFrame (sklearn ColumnTransformer/Scaler)
        X_scaled = scaler.transform(X)

        # אם המודל תומך בקביעה מפורשת של device, ננסה CPU
        if hasattr(model, "set_params"):
            try:
                model.set_params(device='cpu')
            except Exception:
                pass

        preds = model.predict(X_scaled).astype(int)

        if hasattr(model, "predict_proba"):
            probas = model.predict_proba(X_scaled)
            # איתור אינדקס של class=1 (למקרה שסדר הכיתות לא [0,1])
            if hasattr(model, "classes_"):
                class_idx_1 = int(np.where(model.classes_ == 1)[0][0])
            else:
                class_idx_1 = 1
            proba_class_1 = probas[:, class_idx_1]
            proba_class_0 = 1.0 - proba_class_1
        else:
            proba_class_1 = np.full(len(preds), np.nan)
            proba_class_0 = np.full(len(preds), np.nan)

        out = df_raw.copy()
        out["prediction"] = preds
        out["proba_class_0"] = proba_class_0
        out["proba_class_1"] = proba_class_1
        return out

    def post(self, request, *args, **kwargs):
        try:
            # 1) סימבול
            symbol = self._extract_symbol(request.data)
            if not symbol:
                return Response(
                    {'status': 'error', 'message': "Missing 'symbol'/'ticker' in payload."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            try:
                coin = Coin.objects.get(symbol=symbol)
            except ObjectDoesNotExist:
                return Response(
                    {'status': 'error', 'message': f"Symbol '{symbol}' not found."},
                    status=status.HTTP_404_NOT_FOUND
                )

            # 2) נקודת ייחוס – אחרון בזמן
            latest_market = (
                MarketData.objects.filter(symbol=coin)
                .order_by('-close_time')
                .first()
            )
            if not latest_market:
                return Response(
                    {'status': 'error', 'message': f'No market data for {symbol}.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            market_data_id = latest_market.id

            try:
                update_all_technical_features_for_symbol(symbol, market_data_id),
                update_all_sentiment_features_for_symbol(symbol, market_data_id),
            except Exception as e:
                return Response(
                    {'status': 'error', 'message': f'Feature update tasks did not complete: {e}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # 4) פול קצר – שליפת שתי הרשומות באותו timestamp_id
            tech_vals = sent_vals = None
            for _ in range(20):  # ~10 שניות
                # בונה את רשימת השדות לשליפה מה-DB תוך שימוש במילון המיפוי
                tech_fields_to_fetch = [
                    self.MODEL_TO_DB_FIELD_MAP.get(f, f) for f in self.TECH_FEATURES
                ]
                
                tech_vals_raw = (
                    TechnicalFeatures.objects
                    .filter(symbol=coin)
                    .values(*tech_fields_to_fetch)
                    .first()
                )
                
                # מתרגם את המפתחות חזרה לשמות שהמודל מצפה להם
                if tech_vals_raw:
                    tech_vals = {
                        model_field: tech_vals_raw[db_field]
                        for model_field, db_field in self.MODEL_TO_DB_FIELD_MAP.items()
                        if db_field in tech_vals_raw
                    }
                    # מוסיף את שאר הפיצ'רים שלא צריכים תרגום
                    other_tech_fields = [f for f in self.TECH_FEATURES if f not in self.MODEL_TO_DB_FIELD_MAP]
                    tech_vals.update({f: tech_vals_raw[f] for f in other_tech_fields if f in tech_vals_raw})
                else:
                    tech_vals = None

                sent_vals = (
                    SentimentFeatures.objects
                    .filter(symbol=coin)
                    .values(*self.SENT_FEATURES)
                    .first()
                )
                if tech_vals and sent_vals:
                    break
                sleep(0.5)

            if not tech_vals or not sent_vals:
                return Response(
                    {
                        'status': 'error',
                        'message': 'Features missing after computation.',
                        'details': {'expected_timestamp_id': market_data_id}
                    },
                    status=status.HTTP_404_NOT_FOUND
                )

            # 5) הרצת מודל
            row = {**tech_vals, **sent_vals}
            logger.info(f"Raw features for prediction: {row}") # Add logging here
            df = pd.DataFrame([row])
            out_df = self.predict_from_df(df)

            pred = int(out_df["prediction"].iloc[0])
            proba_0 = float(out_df["proba_class_0"].iloc[0])
            proba_1 = float(out_df["proba_class_1"].iloc[0])

            # 6) העשרת ה-payload והפניית סטרטגיה (אם יש URL)
            enriched = request.data.copy()
            enriched['prediction_results'] = {
                'prediction': pred,
                'probabilities': {'class_0': proba_0, 'class_1': proba_1},
                'status': 'success',
                'mode': 'live',
                'timestamp_id': market_data_id
            }

            forwarding_info = {
                'configured_url': STRATEGY_WORKFLOW_URL,
                'status': 'skipped',
                'details': 'No valid STRATEGY_WORKFLOW_URL configured'
            }
            if STRATEGY_WORKFLOW_URL and 'some-default-url' not in STRATEGY_WORKFLOW_URL:
                try:
                    r = requests.post(STRATEGY_WORKFLOW_URL, json=enriched, timeout=10)
                    r.raise_for_status()
                    forwarding_info.update({'status': 'success',
                                            'details': f'Forwarded to {STRATEGY_WORKFLOW_URL}'})
                except requests.exceptions.RequestException as e:
                    forwarding_info.update({'status': 'failed', 'details': str(e)})

            return Response(
                {'status': 'success', 'data': enriched, 'strategy_forwarding': forwarding_info},
                status=status.HTTP_200_OK
            )

        except ValueError as ve:
            return Response({'status': 'error', 'message': f'Feature preparation error: {ve}'},
                            status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        except Exception as e:
            logger.exception("TriggerPredictionView failed")
            return Response({'status': 'error', 'message': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)