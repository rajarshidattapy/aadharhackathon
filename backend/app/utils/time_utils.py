from __future__ import annotations

import pandas as pd


def normalize_date_column(df: pd.DataFrame, date_col: str = "date") -> pd.DataFrame:
    """Parse and standardize a date column.

    - Uses dayfirst=True to accept dd-mm-yyyy and ISO formats.
    - Coerces invalid dates to NaT.
    """

    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col], dayfirst=True, errors="coerce")
    df = df.dropna(subset=[date_col])
    return df


def add_month_column(df: pd.DataFrame, date_col: str, month_col: str = "month") -> pd.DataFrame:
    """Add a month column in YYYY-MM format based on a parsed datetime column."""

    df = df.copy()
    df[month_col] = df[date_col].dt.to_period("M").astype(str)
    return df

