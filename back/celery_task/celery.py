import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

app = Celery('celery_task')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Configure task routing
app.conf.task_routes = {
    'analytics.*': {'queue': 'analytics'},
}

# Configure task monitoring and error handling
app.conf.update(
    task_track_started=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

# Configure periodic tasks
app.conf.beat_schedule = {
    # Analytics tasks
    'update-coin-details-cache': {
        'task': 'analytics.tasks.update_coin_details_cache',
        'schedule': crontab(hour=0, minute=0),  # Run at midnight
    },
    'update_coin_volume_cache': {
        'task': 'analytics.tasks.update_coin_volume_cache',
        'schedule': crontab(hour='0,12', minute=0),  # Run at midnight and noon
    },
    'fetch_missing_klines': {
        'task': 'analytics.tasks.fetch_missing_klines',
        'schedule': crontab(minute='*/30'),  # Run every 30 minutes to fetch new candles
    },
    'fix_missing_coin_data': {
        'task': 'analytics.tasks.fix_missing_coin_data',
        'schedule': crontab(hour='0,12', minute=0),  # Run at midnight and noon
    },
    'fetch-news-sentiment-data': {
        'task': 'analytics.tasks.fetch_news_sentiment_data',
        # Adjust cadence as needed; every 12 hours at minute 0
        'schedule': crontab(minute=0, hour='0,12'),
    },
    
    # Redis tasks
    'cleanup-expired-cache': {
        'task': 'redis.tasks.cleanup_expired_cache',
        'schedule': crontab(hour='0,12', minute=0),  # Run at midnight and noon
    },
}