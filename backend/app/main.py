try:
    # Optional: allow local `backend/.env` (rename from env.example)
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.routers import alerts as alerts_router
from backend.app.routers import ml as ml_router
from backend.app.routers import biometric_alerts as biometric_alerts_router


app = FastAPI(title="Aadhaar Trend-Based Alerting API")

# CORS
# Default: allow any origin (suitable for Streamlit / any hosted frontend).
# Optional: set CORS_ALLOW_ORIGINS to a comma-separated list to restrict.
_cors_origins_raw = os.environ.get("CORS_ALLOW_ORIGINS", "*").strip()
if _cors_origins_raw == "*":
    _cors_allow_origins = ["*"]
else:
    _cors_allow_origins = [o.strip() for o in _cors_origins_raw.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_allow_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Legacy routes: migration + infrastructure related (URRDF, AFLB, ML migration)
app.include_router(
    alerts_router.router,
    prefix="/alerts",
    tags=["Migration / Infra Alerts"],
)
app.include_router(
    ml_router.router,
    prefix="/alerts",
    tags=["Migration / Infra Alerts"],
)

# New biometric routes: BIS + Lost Generation
# NOTE: biometric_alerts router itself already uses prefix="/alerts"
# so we mount it at root to avoid "/alerts/alerts/...".
app.include_router(
    biometric_alerts_router.router,
    tags=["Biometric Alerts"],
)


# Example curl:
#   curl 'http://localhost:8000/health'
#   curl 'http://localhost:8000/alerts/migration'
#   curl 'http://localhost:8000/alerts/infrastructure?month=2023-08'
#   curl 'http://localhost:8000/alerts/migration-ml'
#   curl 'http://localhost:8000/alerts/biometric-integrity'
#   curl 'http://localhost:8000/alerts/lost-generation'


@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    """Simple health check endpoint."""
    return {"status": "ok"}

