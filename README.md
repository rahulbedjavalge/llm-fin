# LLM Financial Statement Copilot (MVP)

An MVP web app that:
- Parses uploaded financial statements (CSV/XLSX) into a normalized schema.
- Computes key ratios and simple red flags.
- Produces a direction/risk assessment and explanation (LLM-like heuristic placeholder).
- Benchmarks against a simple baseline model (logistic regression) on synthetic features.

## Stack
- Backend: FastAPI (Python) + pandas + scikit-learn
- Frontend: React (Vite + TypeScript)

## Quickstart (Windows PowerShell)

### 1) Backend
```powershell
# from repo root
python -m venv .venv
. .venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt

# Optional: create .env from example and add your keys if integrating a real LLM
Copy-Item backend/.env.example backend/.env

# Run API
python -m uvicorn backend.main:app --reload --port 8000
```
Visit http://127.0.0.1:8000/docs for interactive API.

### 2) Frontend
```powershell
# from repo root
cd frontend
npm install
npm run dev
```
Open the URL shown by Vite (usually http://127.0.0.1:5173).

## Endpoints
- POST /upload: Upload CSV/XLSX; parses and returns ratios + red flags for latest row.
- GET /ratios: Returns last computed ratios.
- GET /baseline: Returns baseline prediction for last ratios.
- POST /analyze: Returns heuristic "LLM" analysis + baseline + agreement flag.
- GET /health: Health check.

## Data Schema (normalized)
{ ticker, period, revenue, cogs, sga, operating_income, net_income, total_assets, total_liabilities, equity, cash, receivables, inventory }

A tiny sample is provided at data/sample_financials.csv.

## Evaluation (toy)
Run a tiny evaluation on the sample and heuristic baseline:
```powershell
python scripts/evaluate.py
```

## Governance & Safety Notes (MVP)
- This project is for demonstration only; not investment advice.
- Outputs include simple uncertainty suggestions (risk levels via leverage heuristics).
- Prompts/providers should explicitly avoid demographic attributes in decisioning.

## Research Hook (for LinkedIn)
- Inspired by recent work exploring LLMs for financial statement analysis and comparisons to ML baselines on structured fundamentals; and by studies auditing explanation faithfulness (e.g., SHAP) in credit/risk.

## LinkedIn Draft
"Built a research-aligned LLM copilot that ingests standardized financial statements, computes key ratios, predicts earnings direction/risk, and explains the rationale—benchmarked against a simple logistic regression baseline. Stack: FastAPI + React + scikit-learn. Includes a tiny evaluation pipeline and a synthetic case (Company X)."

## Next Steps
- Swap heuristic LLM with a real provider (env-configured adapter in backend/llm.py).
- Add SHAP comparisons for baseline and expand datasets.
- Improve dataset coverage and benchmarking protocol.
