# ShadowLight

## Repo structure

```
.
├─ app/
│  ├─ main.py
│  ├─ routers/
│  │  ├─ metrics.py
│  │  └─ agent.py
│  ├─ schemas/
│  │  ├─ metrics.py
│  │  └─ agent.py
│  └─ utils/
│     ├─ database.py
│     ├─ agent.py
│     └─ queries.py
├─ models/
│  ├─ ads_metrics_daily.sql
│  ├─ ads_metrics_last_30_vs_prior.sql
│  └─ sources.yml
├─ dbt_project.yml
├─ requirements.txt
├─ update_wh.py
└─ vanna.ipynb
```

Key pieces:

- **FastAPI app**: `app/main.py` mounts two routers: `/metrics` (analytics) and `/ask` (Vanna LLM SQL).
- **Metrics router**: `/metrics/dates` with pagination & validation via Pydantic models.
- **LLM router**: `/ask` accepts a natural-language question, calls Vanna to generate SQL, runs it on DuckDB, and returns JSON.
- **DB access**: local DuckDB file `data/warehouse/db.duckdb` (path resolved relative to `app/`).
- **dbt project**: models compute daily CAC/ROAS and a 30-day vs prior 30-day rollup; sources expect `raw.ads_spend`.
- **Data loader**: `update_wh.py` demonstrates loading a CSV into DuckDB as `ads_spend`.

## Requirements

Python packages are pinned in `requirements.txt`:

```
dbt-duckdb==1.9.4
fastapi==0.116.1
openai==1.102.0
pandas==2.3.2
uvicorn==0.35.0
vanna==0.7.9
```

> Tip: Use a virtual environment (`python -m venv .venv && source .venv/bin/activate`) to avoid system Python conflicts (PEP 668).

## Quickstart

### 1) Clone & environment

```bash
git clone https://github.com/smm-0216/test_shadowlight.git
cd test_shadowlight

# create and activate a venv
python -m venv .venv
# Windows
. .venv/Scripts/activate
# macOS/Linux
# source .venv/bin/activate

# install deps
pip install -r requirements.txt
```

### 2) Configure environment variables

The LLM agent uses Vanna + OpenAI keys read from env vars:

```bash
# required
export VANNA_MODEL="shadowlight-or-your-model"
export VANNA_API_KEY="..."
export OPENAI_KEY="sk-..."

# Windows (PowerShell)
# $env:VANNA_MODEL="shadowlight-or-your-model"
# $env:VANNA_API_KEY="..."
# $env:OPENAI_KEY="sk-..."
```

These are referenced in `app/utils/agent.py`.

### 3) Prepare the DuckDB warehouse (via n8n workflow)

This repo includes an **n8n workflow** that builds/loads the warehouse table **`raw.ads_spend`** into your local DuckDB at `data/warehouse/db.duckdb`.

**What you need first**  
- n8n running locally (Desktop app or Docker). Two common options:

**Option A — n8n Desktop (easiest)**  
1) Install n8n Desktop (Windows/macOS/Linux).  
2) Open n8n and go to **Workflows → Import from File**.  
3) Select the file **`Test ShadowLight.json`** from this repo.  
4) Open the imported workflow and review the nodes that reference file paths or DuckDB paths. Update them if needed to match your local repo path (e.g., `data/warehouse/db.duckdb` and any CSV/input locations the workflow expects).  
5) Click **Execute** (manual) or **Activate** (to schedule).  
6) After a successful run, you should have the table `raw.ads_spend` available in your DuckDB database.

**Option B — n8n in Docker**  
```bash
docker run -it --rm   -p 5678:5678   -v ~/.n8n:/home/node/.n8n   -v "$PWD":/project   n8nio/n8n:latest
```
Then open **http://localhost:5678**, go to **Workflows → Import from File**, choose **`/project/Test ShadowLight.json`**, adjust any local paths/credentials, and run it.

> Notes
> - The workflow is the **single source of truth** for staging/loading. Do **not** run the previous manual DuckDB loader code or direct SQL COPY in this step.  
> - Make sure the workflow writes to schema **`raw`** and table **`ads_spend`** to align with `models/sources.yml`.
> - If you want to automate refreshes, set a **Cron** trigger in the workflow and keep n8n running.

When the workflow completes, proceed to dbt.

### 4) Configure dbt (DuckDB profile)

Create or update your `~/.dbt/profiles.yml`:

```yaml
shadowlight:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: /absolute/path/to/repo/data/warehouse/db.duckdb
      schema: raw
```

Project config (already in the repo):

```yaml
# dbt_project.yml
name: "shadowlight"
version: "1.0.0"
config-version: 2
profile: "shadowlight"
model-paths: ["models"]
```

### 5) Build dbt models

```bash
dbt run
```

This will materialize:

- `ads_metrics_daily` — daily spend, conversions, CAC, ROAS (table materialization)  
- `ads_metrics_last_30_vs_prior` — aggregates last 30 vs prior 30 days
- `ads_metrics_compact` — pivots the table and adds deltas

### 6) Run the API

```bash
uvicorn app.main:app --reload
# API on http://127.0.0.1:8000
```

The app wires up both routers in `main.py`.

## API

### GET `/metrics/dates`

Query params:

- `start` (YYYY-MM-DD)
- `end` (YYYY-MM-DD)
- `page` (default `1`)
- `page_size` (default `50`, max `1000`)

Response (example shape):

```json
{
  "count": 50,
  "page": 1,
  "page_size": 50,
  "total": 1234,
  "has_prev": false,
  "has_next": true,
  "data": [
    { "date": "2025-08-01", "spend": 123.45, "conversions": 6, "cac": 20.575, "roas": 4.86 }
  ]
}
```

**Curl:**
```bash
curl "http://127.0.0.1:8000/metrics/dates?start=2025-07-01&end=2025-07-31&page=1&page_size=50"
```

### POST `/ask`

Body:
```json
{ "question": "Show total spend and CAC for July 2025" }
```

Behavior:
- `Agent` (Vanna + OpenAI) generates SQL from your question,  
- SQL is executed against DuckDB,  
- Returns either records or `"No data found for your question."`  

**Curl:**
```bash
curl -X POST "http://127.0.0.1:8000/ask/"   -H "Content-Type: application/json"   -d '{"question":"Show total spend and CAC for the last 7 days"}'
```

## Implementation notes

- **Database pathing**: `Database` computes `db.duckdb` relative to the repo (`data/warehouse/db.duckdb`). Ensure the file exists before you hit the API.
- **Validation**: `MetricsParams` enforces `start <= end`, pagination, and bounds.
- **Materializations & sources**: `ads_metrics_daily` is explicitly `materialized='table'`; sources define `raw.ads_spend`.

## Local development checklist

1. `python -m venv .venv && source .venv/bin/activate`  
2. `pip install -r requirements.txt`  
3. Set `VANNA_MODEL`, `VANNA_API_KEY`, `OPENAI_KEY`.  
4. Load `raw.ads_spend` into `data/warehouse/db.duckdb`.  
5. `dbt run` to build models.  
6. `uvicorn app.main:app --reload`

## Troubleshooting

- **No data from `/metrics/dates`** → Confirm `raw.ads_spend` exists and date range has rows.  
- **LLM errors** → Verify `VANNA_MODEL`, `VANNA_API_KEY`, and `OPENAI_KEY` are set.  
- **dbt profile** → Ensure `profiles.yml` points to the correct absolute `path` for DuckDB.  
