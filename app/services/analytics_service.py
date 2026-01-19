from __future__ import annotations

from typing import Optional

import pandas as pd

from app.analytics.aflb import compute_aflb_alerts
from app.analytics.urrdf import compute_urrdf_alerts
from app.core.data_loader import DataValidationError, get_dataset


class AnalyticsService:
    """Service layer orchestrating data loading and analytics computations."""

    def __init__(self) -> None:
        # In a more complex app, dependencies could be injected here
        pass

    def _get_base_df(self) -> pd.DataFrame:
        return get_dataset()

    def urrdf_alerts(self, month: Optional[str] = None):
        df = self._get_base_df()
        return compute_urrdf_alerts(df, month=month, top_n=10)

    def aflb_alerts(self, month: Optional[str] = None):
        df = self._get_base_df()
        return compute_aflb_alerts(df, month=month, top_n=20)


analytics_service = AnalyticsService()

