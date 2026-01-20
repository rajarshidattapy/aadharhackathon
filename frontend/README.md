# Aadhaar Alert Analytics Dashboard

## Quick Start

### 1. Start the FastAPI Backend
```bash
# from the repository root
pip install -r backend/requirements.txt
hypercorn backend.app.main:app --bind 0.0.0.0:8001
```

### 2. Run the Streamlit Dashboard
```bash
cd frontend
pip install -r requirements.txt
export BACKEND_URL="http://127.0.0.1:8001"
streamlit run app.py
```

The dashboard will open at `http://localhost:8501`

## Deployment (Streamlit Community Cloud)
- **Main file**: `frontend/app.py`
- **Dependencies**: `frontend/requirements.txt`
- **Secrets / env**: set `BACKEND_URL` in Streamlit Cloud settings (or create a local `.env` by copying `frontend/env.example`)

## Features
- 6 analytics pages: Overview, Migration, Infrastructure, Biometric, Lost Generation, ML Forecast
- Interactive Plotly charts with filtering
- CSV download for all data tables
- Responsive sidebar with global filters

