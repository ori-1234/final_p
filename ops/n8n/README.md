ops/n8n – n8n flows (do NOT store secrets)

Structure:
- flows/          Put exported workflow JSON files here
- scripts/        Optional helper scripts (import/export)
- credentials/    Do NOT commit real credentials; docs only

Safety:
- Your live flows inside the n8n container remain in its volume (/home/node/.n8n).
- This repo only mounts flows/ read-only into the container for safe import.
- You control when to import/export; nothing auto-overwrites.

Import (from host):
- With the provided compose mount, run inside the container:
  n8n import:workflow --separate --input /project/ops/n8n/flows

Export (optional backup to repo):
- Export to a temp dir then copy out, or script it later.

Security notes:
- Do NOT hardcode API keys in JSON flows. Use n8n Credentials or env refs.
- Replace any keys in these JSONs with placeholders. Store secrets only in n8n credentials or .env (not committed).


Flows overview and required keys
--------------------------------

sentiment_analysis.json
- What it does: Fetches latest news for a symbol from Newsdata, performs LLM-based sentiment analysis, aggregates daily metrics (score/label/topic_counts/top_articles). Optional nodes (disabled by default) can write results to Postgres.
- Triggers: Manual or via enabling a Webhook node (disabled by default).
- Output: Daily sentiment JSON object(s).
- Required configuration:
  - Environment variables in n8n:
    - NEWSDATA_API_KEY (required)
    - NEWSDATA_ENDPOINT (optional; default https://newsdata.io/api/1/latest)
  - n8n Credentials:
    - OpenAI API (for LLM/Agent nodes)
    - Postgres (only if you enable the DB write nodes)

technical_analysis.json
- What it does: Pulls indicators from TwelveData (SMA/EMA/RSI/MACD/ATR/BBANDS), fetches Binance klines (public endpoint), computes Fibonacci and support/resistance, and runs an LLM-based technical analysis.
- Triggers: Manual (executeWorkflowTrigger).
- Output: Unified technical analysis JSON.
- Required configuration:
  - Environment variables in n8n:
    - TWELVEDATA_API_KEY (required)
  - n8n Credentials:
    - OpenAI API
  - Notes: Binance klines endpoint used here is public (no key required). There is a disabled HTTP Request node to post results back to the backend; enable and point it to your backend only if you need that flow.

strategy_analysis.json
- What it does: Merges sentiment and technical data, optionally uses RAG tools, and produces a multi-timeframe strategy via LLM. Posts the final combined payload back to the backend.
- Triggers: Internal trigger (executeWorkflowTrigger). A Webhook node exists but is disabled by default; you can expose it and configure the backend to call it.
- Output: Strategy JSON posted to the backend.
- Required configuration:
  - Environment variables in n8n:
    - BACKEND_N8N_WEBHOOK_URL (required; endpoint to post results to the backend)
    - SUPABASE_EDGE_FUNC_URL (optional; only if you enable the RAG HTTP tool)
  - n8n Credentials (optional features):
    - OpenAI API (required)
    - Supabase (URL + KEY) if you enable vector store or RAG tools

RAG.json (optional)
- What it does: Demonstrates a RAG pipeline (Google Drive PDF → clean/summarize → chunk → embeddings → store in Supabase vector store).
- Required configuration:
  - n8n Credentials:
    - Google Drive OAuth2
    - OpenAI API (LLM + embeddings)
    - Supabase (URL + KEY) for the vector store
- Not needed for the core app; use only if you plan to leverage RAG.


Backend integration (Django)
---------------------------
- If you enable inbound webhooks in n8n flows, set the corresponding backend env vars so the backend can call n8n or receive posts from it:
  - N8N_SENTIMENT_ANALYSIS_URL (optional; backend → n8n sentiment webhook if you enable it)
  - N8N_STRATEGY_WORKFLOW_URL (optional; backend → n8n strategy webhook if you enable it)
- The strategy flow already posts back to the backend using BACKEND_N8N_WEBHOOK_URL (configured in n8n ENV).


Environment variables summary (no secrets here)
----------------------------------------------
- In n8n container ENV:
  - NEWSDATA_API_KEY (required for sentiment)
  - NEWSDATA_ENDPOINT (optional)
  - TWELVEDATA_API_KEY (required for technical)
  - BACKEND_N8N_WEBHOOK_URL (required for strategy flow POST back)
  - SUPABASE_EDGE_FUNC_URL (optional; RAG tool)
- In backend ENV (if using webhooks):
  - N8N_SENTIMENT_ANALYSIS_URL (optional)
  - N8N_STRATEGY_WORKFLOW_URL (optional)


Quickstart checklist for n8n
----------------------------
1) Open n8n UI (default http://localhost:5678; change credentials in compose/ENV for production).
2) Create Credentials:
   - OpenAI API
   - (Optional) Postgres
   - (Optional) Supabase
   - (Optional) Google Drive
3) Set ENV on the n8n container (compose or platform):
   - NEWSDATA_API_KEY, TWELVEDATA_API_KEY, BACKEND_N8N_WEBHOOK_URL (and any optional ones you need).
4) Import flows:
   - n8n import:workflow --separate --input /project/ops/n8n/flows
5) (Optional) Enable any Webhook nodes you want to expose and update backend envs accordingly.


Production notes
----------------
- Never commit real credentials. Use n8n Credentials or container/platform secrets.
- Lock down n8n basic auth (N8N_BASIC_AUTH_USER / N8N_BASIC_AUTH_PASSWORD) and restrict external exposure.
- Keep flows minimal; externalize all tokens/URLs to ENV or Credentials.
