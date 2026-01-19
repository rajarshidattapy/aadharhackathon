from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.core.data_loader import DataValidationError
from app.schemas.alerts import AFLBAlert, AFLBAlertsResponse, ErrorResponse, URRDFAlert, URRDFAlertsResponse
from app.services.analytics_service import analytics_service


router = APIRouter()


@router.get(
    "/migration",
    response_model=URRDFAlertsResponse,
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def get_migration_alerts(month: Optional[str] = Query(None, description="Target month in YYYY-MM format")) -> URRDFAlertsResponse:
    """Return URRDF (Urban Readiness & Resource Demand Forecast) alerts.

    If `month` is not provided, the latest available month in the dataset is used.
    """

    try:
        df = analytics_service.urrdf_alerts(month=month)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except DataValidationError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    if df.empty:
        raise HTTPException(status_code=404, detail="No URRDF alerts available for the requested month")

    # Determine response month from data
    response_month = df["month"].iloc[0]

    alerts = [
        URRDFAlert(
            state=row["state"],
            district=row["district"],
            month=row["month"],
            inflow_score=float(row["inflow_score"]),
            level=row["level"],
            predicted_pressure=list(row["predicted_pressure"]),
            recommendations=list(row["recommendations"]),
        )
        for _, row in df.iterrows()
    ]

    return URRDFAlertsResponse(month=response_month, alerts=alerts)


@router.get(
    "/infrastructure",
    response_model=AFLBAlertsResponse,
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def get_infrastructure_alerts(month: Optional[str] = Query(None, description="Target month in YYYY-MM format")) -> AFLBAlertsResponse:
    """Return AFLB (Aadhaar Facility Load Balancer) alerts.

    If `month` is not provided, the latest available month in the dataset is used.
    """

    try:
        df = analytics_service.aflb_alerts(month=month)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except DataValidationError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    if df.empty:
        raise HTTPException(status_code=404, detail="No AFLB alerts available for the requested month")

    response_month = df["month"].iloc[0]

    alerts = [
        AFLBAlert(
            state=row["state"],
            district=row["district"],
            pincode=str(row["pincode"]),
            month=row["month"],
            total_load=int(row["total_load"]),
            stress_score=float(row["stress_score"]),
            tier=row["tier"],
            recommendations=list(row["recommendations"]),
        )
        for _, row in df.iterrows()
    ]

    return AFLBAlertsResponse(month=response_month, alerts=alerts)

