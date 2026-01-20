from __future__ import annotations

from typing import List, Optional

import pandas as pd


URRDF_PREDICTED_PRESSURE = [
    "PDS",
    "Public Health",
    "Housing",
    "Aadhaar Centers",
]


def compute_urrdf_alerts(df: pd.DataFrame, month: Optional[str] = None, top_n: int = 10) -> pd.DataFrame:
    """Compute URRDF alerts.

    - Aggregates monthly by (state, district, month).
    - demo_total_adult = demo_age_17_
    - inflow_score = current_month / avg(last_3_months) per (state, district).
    - Returns top_n districts for the specified or latest month.
    """

    work = df.copy()

    # Aggregate at monthly granularity
    agg = (
        work.groupby(["state", "district", "month"], as_index=False)[["demo_age_17_"]]
        .sum()
        .rename(columns={"demo_age_17_": "demo_total_adult"})
    )

    # Sort to ensure correct rolling window per group
    agg = agg.sort_values(["state", "district", "month"])  # month is YYYY-MM string

    # For rolling, convert month to a proper PeriodIndex within each group
    def _compute_group(g: pd.DataFrame) -> pd.DataFrame:
        g = g.sort_values("month")
        # Use a numeric index for rolling
        g = g.reset_index(drop=True)
        # Compute rolling mean of last 3 months excluding current (shift)
        rolling_mean = (
            g["demo_total_adult"].rolling(window=3, min_periods=1).mean().shift(1)
        )
        g["rolling_avg_demo_total_adult"] = rolling_mean
        # Avoid division by zero
        denom = g["rolling_avg_demo_total_adult"].replace({0: pd.NA})
        g["inflow_score"] = (g["demo_total_adult"] / denom).fillna(0.0)
        return g

    agg = agg.groupby(["state", "district"], group_keys=False).apply(_compute_group)

    # Determine target month (latest if not provided)
    if month is None:
        latest_month = agg["month"].max()
    else:
        latest_month = month

    month_df = agg[agg["month"] == latest_month].copy()

    if month_df.empty:
        # If requested month has no data, just return empty frame
        return month_df

    # Determine alert level
    def _level(score: float) -> str:
        if score > 1.8:
            return "SURGE"
        if 1.3 <= score <= 1.8:
            return "HEAVY"
        if 1.0 <= score < 1.3:
            return "NORMAL"
        return "NORMAL"  # scores below 1 treated as normal for now

    def _recs(level: str) -> List[str]:
        if level == "SURGE":
            return [
                "Open 2 temporary enrollment/update camps",
                "Deploy mobile Aadhaar van",
                "Increase ration shop capacity",
                "Set up drinking water + shade",
            ]
        if level == "HEAVY":
            return [
                "Increase staff shifts for 14 days",
                "Add multilingual helpdesk",
            ]
        return ["Monitor trends"]

    month_df["level"] = month_df["inflow_score"].apply(_level)
    month_df["predicted_pressure"] = [URRDF_PREDICTED_PRESSURE] * len(month_df)
    month_df["recommendations"] = month_df["level"].apply(_recs)

    # Sort and trim
    month_df = month_df.sort_values("inflow_score", ascending=False).head(top_n)

    # Round inflow_score for presentation
    month_df["inflow_score"] = month_df["inflow_score"].round(2)

    return month_df[[
        "state",
        "district",
        "month",
        "demo_total_adult",
        "inflow_score",
        "level",
        "predicted_pressure",
        "recommendations",
    ]]

