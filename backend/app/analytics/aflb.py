from __future__ import annotations

from typing import List, Optional

import pandas as pd


def compute_aflb_alerts(df: pd.DataFrame, month: Optional[str] = None, top_n: int = 20) -> pd.DataFrame:
    """Compute AFLB alerts.

    - Aggregates monthly by (state, district, pincode, month).
    - enrol_total = age_0_5 + age_5_17 + age_18_greater
    - demo_total  = demo_age_5_17 + demo_age_17_
    - bio_total   = bio_age_5_17 + bio_age_17_
    - total_load  = enrol_total + demo_total + bio_total
    - stress_score = current_month / avg(last_3_months) per (state, district, pincode).
    """

    work = df.copy()

    # Pre-compute component totals
    work["enrol_total"] = (
        work["age_0_5"] + work["age_5_17"] + work["age_18_greater"]
    )
    work["demo_total"] = work["demo_age_5_17"] + work["demo_age_17_"]
    work["bio_total"] = work["bio_age_5_17"] + work["bio_age_17_"]
    work["total_load"] = work["enrol_total"] + work["demo_total"] + work["bio_total"]

    agg = (
        work.groupby(["state", "district", "pincode", "month"], as_index=False)[["total_load"]]
        .sum()
    )

    agg = agg.sort_values(["state", "district", "pincode", "month"])

    def _compute_group(g: pd.DataFrame) -> pd.DataFrame:
        g = g.sort_values("month")
        g = g.reset_index(drop=True)
        rolling_mean = g["total_load"].rolling(window=3, min_periods=1).mean().shift(1)
        g["rolling_avg_total_load"] = rolling_mean
        denom = g["rolling_avg_total_load"].replace({0: pd.NA})
        g["stress_score"] = (g["total_load"] / denom).fillna(0.0)
        return g

    agg = agg.groupby(["state", "district", "pincode"], group_keys=False).apply(_compute_group)

    # Determine target month
    if month is None:
        latest_month = agg["month"].max()
    else:
        latest_month = month

    month_df = agg[agg["month"] == latest_month].copy()

    if month_df.empty:
        return month_df

    def _tier(score: float) -> str:
        if score > 2.0:
            return "CRITICAL"
        if 1.5 <= score <= 2.0:
            return "HIGH"
        if 1.2 <= score < 1.5:
            return "WATCH"
        return "NORMAL"

    def _recs(tier: str) -> List[str]:
        if tier == "CRITICAL":
            return [
                "Set up drinking water points",
                "Shade + seating arrangement",
                "Token queue system",
                "Basic medical support",
                "Volunteer/police crowd management",
                "Mobile vans to split the load",
            ]
        if tier == "HIGH":
            return [
                "Add temporary Aadhaar camp (school/community hall)",
                "Deploy 2-3 extra kits",
                "Add queue tokens + helpdesk",
            ]
        if tier == "WATCH":
            return [
                "Extend working hours",
                "Enable appointment scheduling",
                "Add 1 extra operator temporarily",
            ]
        return ["No action required"]

    month_df["tier"] = month_df["stress_score"].apply(_tier)
    month_df["recommendations"] = month_df["tier"].apply(_recs)

    month_df = month_df.sort_values("stress_score", ascending=False).head(top_n)

    month_df["stress_score"] = month_df["stress_score"].round(2)
    month_df["total_load"] = month_df["total_load"].astype(int)

    return month_df[[
        "state",
        "district",
        "pincode",
        "month",
        "total_load",
        "stress_score",
        "tier",
        "recommendations",
    ]]

