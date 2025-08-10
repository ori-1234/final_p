from django.urls import path
from .views import N8NWebhookReceiver, GetAnalysisResult, TriggerPredictionView

urlpatterns = [
    path('n8n-webhook/', N8NWebhookReceiver.as_view(), name='n8n-webhook'),
    path('n8n-prediction-webhook/', TriggerPredictionView.as_view(), name='n8n-prediction-webhook'),
    path('get-analysis-result/<str:symbol>/', GetAnalysisResult.as_view(), name='get-analysis-result'),
]
 