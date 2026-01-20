# Backend (Render)

## Local run

```bash
cd backend
pip install -r requirements.txt
hypercorn backend.app.main:app --bind 0.0.0.0:8001
```

Optional env vars (copy `backend/env.example` to `.env` locally):
- `AADHAAR_DATA_FILE`: CSV path for the main dataset used by migration/infra analytics
- `AADHAAR_MERGED_CSV`: CSV path used by BIS / Lost Generation analytics

## Deploy on Render

This repo includes a Render blueprint at `render.yaml`.

- **Root directory**: `backend`
- **Runtime**: Docker (uses `backend/Dockerfile`)

Set env vars in Render dashboard if you want to point at a dataset file:
- `AADHAAR_DATA_FILE`
- `AADHAAR_MERGED_CSV`

