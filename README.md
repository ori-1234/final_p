System - Full Project Documentation

A full-stack crypto analytics platform combining a Django backend (REST, Celery, Channels, Redis, Postgres), a React (Vite) frontend, and optional n8n integration for news/sentiment ingestion. The system ingests market data (Binance klines), computes technical and sentiment features, provides analysis endpoints and a prediction trigger, and serves a modern UI.

## Table of Contents
- Architecture
- Services
- Backend Overview
- Frontend Overview
- Environment Variables
- Quickstart with Docker
- Initialization Orchestrator
- Alternative: Local (without Docker) Setup
- Data Flows
- Key API Endpoints
- Common Operations
- Troubleshooting
- Production Notes

## Architecture

frontend (Vite/React)
  <-> HTTP (CORS 5173 -> 8000)
backend (Django + DRF + Channels)
  - PostgreSQL (market data, features, users)
  - Redis (cache, channels layer, celery broker/backend)
  - Celery workers (analytics + default queues)
  - Optional n8n (webhooks for sentiment/news)

- Market data source: Binance klines (12h candles)
- Technical indicators: ta library
- Feature stores: analysis.TechnicalFeatures, analysis.SentimentFeatures
- Caching: Redis for chart and volume series
- Realtime: Channels/Redis, Binance WebSocket consumer on app ready

## Services

Defined in docker-compose.yml:

- frontend: Vite dev server on http://localhost:5173 (depends on backend)
- backend: Django on http://localhost:8000
- db: Postgres 15 (exposes 5432)
- redis: Redis 7 (exposes 6379)
- celery: Celery worker (-Q celery,analytics)
- n8n: Optional workflow system on http://localhost:5678 (admin/admin123)
  - Use .env to supply credentials; defaults in compose are placeholders only

## Backend Overview

- Django project: back/backend with apps: user, analytics, analysis, celery_task
- Settings: Postgres, Channels/Redis, DRF auth via cookies (simplejwt), CORS for 5173, Celery via Redis
- Models:
  - analytics.Coin, analytics.MarketData (12h OHLCV, indicators, unique on symbol+close_time)
  - analysis.TechnicalFeatures, analysis.SentimentFeatures
  - analytics.DailySentimentData, analytics.NewsSentimentData (optional via n8n)
- Tasks:
  - analytics.tasks.fetch_missing_klines (12h), initialize_all_coins_historical_data
  - analytics.tasks.update_coin_details_cache, update_coin_volume_cache
  - analysis.tasks.update_all_technical_features_for_symbol, update_all_sentiment_features_for_symbol
- App init (analytics.apps.AnalyticsConfig.ready): clears cache, dispatches klines fetch, starts websocket consumer

## Frontend Overview

- Vite + React on port 5173
- VITE_API_URL points to backend http://localhost:8000
- Pages/components for dashboard, coin views, analysis UI, auth context

## Environment Variables

Important (provided via .env; do not commit real secrets, commit only .env.example):

- Django: DJANGO_SECRET_KEY, DEBUG, ALLOWED_HOSTS
- Database: DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
- Redis/Celery: REDIS_HOST, REDIS_PORT, REDIS_DB
- n8n: N8N_BASE_URL, N8N_WEBHOOK_SECRET, N8N_SENTIMENT_ANALYSIS_URL, N8N_BASIC_AUTH_USER, N8N_BASIC_AUTH_PASSWORD
  - BACKEND_N8N_WEBHOOK_URL (for n8n flow -> backend webhook)
  - NEWSDATA_API_KEY/NEWSDATA_ENDPOINT (used in flows)
  - TWELVEDATA_API_KEY (used in technical analysis flow)
  - BACKEND_PREDICTION_WEBHOOK_URL (optional; technical flow → backend prediction webhook)
  - ADMIN_USERNAME/ADMIN_EMAIL/ADMIN_PASSWORD (backend superuser on first run)

## Quickstart with Docker

Prerequisites: Git, Docker Desktop (Compose v2)

1) Clone repo and start base services:

```
git clone <your_repo_url> system
cd system
docker compose up -d db redis n8n
```

2) Start database (with auto-init), backend (auto-migrate + create admin), celery, frontend:

```
docker compose build backend celery frontend db
docker compose up -d db redis
# Optional: place a dump at db/*.sql to auto-restore on first run (mounted to /docker-entrypoint-initdb.d)
docker compose up -d backend celery frontend
```

3) Initialize the system with the orchestrator (recommended):

```
# Full flow: migrate, seed, deep backfill (456d, 12h), compute tech features, warm caches
docker compose exec backend python back/init_orchestrator.py --all

# Optionally also seed detailed coins metadata
docker compose exec backend python back/init_orchestrator.py --seed-detailed-coins
```

4) Open services:
- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- n8n: http://localhost:5678 (use credentials from .env; do not commit real secrets)

## Initialization Orchestrator

Single command runner at back/init_orchestrator.py centralizes setup and data flows.

Flags:

```
--coins SYMBOLS...            (default: BTC ETH SOL XRP LTC)
--migrate                     (apply migrations)
--seed-coins                  (seed basic coin list)
--seed-detailed-coins         (seed/update detailed coin metadata)
--use-given-ids               (preserve provided ids for new rows when seeding detailed coins)
--superuser                   (create admin/admin)
--deep-backfill-days N        (backfill N days, 12h candles, with indicators)
--compute-tech                (compute and save technical features)
--compute-sent                (compute and save sentiment features; requires DailySentimentData)
--fetch-sentiment-n8n         (trigger n8n webhook)
--warm-caches                 (cache chart/volume data)
--all                         (migrate, seed, deep backfill 456d, compute tech, warm caches)
```

Examples:

```
# Full init (market + tech features + caches)
docker compose exec backend python back/init_orchestrator.py --all

# Seed detailed coin metadata
docker compose exec backend python back/init_orchestrator.py --seed-detailed-coins --use-given-ids

# Backfill 200 days and compute features
docker compose exec backend python back/init_orchestrator.py --deep-backfill-days 200 --compute-tech --warm-caches

# Sentiment (requires n8n flow and DailySentimentData)
docker compose exec backend python back/init_orchestrator.py --fetch-sentiment-n8n
# After your flow populated data:
docker compose exec backend python back/init_orchestrator.py --compute-sent
```

## Alternative: Local (without Docker) Setup

Run infra in Docker (db/redis/n8n) and the backend locally, or run everything locally.

Backend (local venv):

```
cd back
python -m venv venv
venv\\Scripts\\activate            # Windows
# source venv/bin/activate         # macOS/Linux
pip install -r requirements.txt
set DJANGO_SETTINGS_MODULE=backend.settings
# export DJANGO_SETTINGS_MODULE=backend.settings

# If you use dockerized db/redis:
set DB_HOST=localhost & set DB_PORT=5432
set REDIS_HOST=localhost & set REDIS_PORT=6379

python manage.py migrate
python manage.py runserver 0.0.0.0:8000
celery -A celery_task worker -l info -Q celery,analytics
```

Frontend (local):

```
cd front
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

## Data Flows

- Historical and missing klines (12h) via analytics.tasks.fetch_missing_klines and/or orchestrator deep backfill
- Technical indicators computed with ta and persisted alongside market data; feature engineering saved in analysis.TechnicalFeatures
- Sentiment (optional): n8n webhook populates analytics.DailySentimentData/NewsSentimentData; analysis.tasks.update_all_sentiment_features_for_symbol computes features
- Cache warm-up: chart and volume daily series saved in Redis for fast UI

Backend startup: analytics.apps.AnalyticsConfig.ready clears cache, dispatches initial klines fetch, starts a Binance WebSocket consumer.

## Important Code References

- Prediction pipeline (feature preparation and model inference):
  - back/analysis/views.py → `TriggerPredictionView` and helpers
    - Prepares technical and sentiment features, loads scaler and model, and performs prediction.
  - back/analysis/ML_model/chosen_model.py → model selection utilities

- Sentiment aggregation and tasks:
  - back/analytics/tasks.py → fetch/update tasks, sentiment aggregation (`aggregate_daily_sentiment`)

- Caching layer:
  - back/redis_cache/cache_utils/* → cache utilities for analysis/market/user

- Orchestration:
  - back/init_orchestrator.py → migrate/seed/backfill/compute features, and admin creation.

## Key API Endpoints

Some endpoints are intentionally open (webhooks). Auth uses cookie-based JWT by default.

- Analysis (in back/analysis/views.py):
  - POST /analysis/webhook/ – receive n8n analysis payload and cache it
  - GET  /analysis/result/{symbol}/ – fetch cached analysis data
  - POST /analysis/predict/ – trigger computation (tech+sent) for latest market record; run model (mock if assets missing); forward to strategy workflow

## Common Operations

- Migrations: docker compose exec backend python manage.py migrate --noinput
- Superuser: docker compose exec backend python manage.py createsuperuser (or orchestrator --superuser)
- Seed coins: basic --seed-coins, detailed --seed-detailed-coins [--use-given-ids]
- Backfill market data (12h): --deep-backfill-days N
- Compute features: tech --compute-tech, sentiment --compute-sent
- Warm caches: --warm-caches

## Troubleshooting

- Postgres not ready: ensure db is healthy. docker compose restart db backend celery
- Celery tasks not running: check celery logs/queues. Ensure Redis broker/result envs.
- CORS errors: ensure frontend uses http://localhost:5173 and VITE_API_URL -> http://localhost:8000
- n8n: verify N8N_SENTIMENT_ANALYSIS_URL and login (admin/admin123)
- Empty features after backfill: ensure ta installed; for sentiment ensure DailySentimentData exists

## Production Notes

- Set strong secrets and DEBUG=False
- Restrict CORS/CSRF and ALLOWED_HOSTS
- Externalize env via .env
- Add dedicated celery-beat service for periodic tasks
- Manage Postgres volumes/backups
- Serve frontend as static build behind reverse proxy

## Useful URLs

- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- n8n: http://localhost:5678

## License

Proprietary – internal use unless specified otherwise.


