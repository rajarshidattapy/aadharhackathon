from typing import List

import pandas as pd


KEY_COLS: List[str] = ["date", "state", "district", "pincode"]


def _strip_text_column(df: pd.DataFrame, col: str) -> None:
    """Strip whitespace from a text column in-place if it exists."""
    if col in df.columns:
        df[col] = df[col].astype("string").str.strip()


def clean_and_aggregate(
    df: pd.DataFrame,
    date_col: str = "date",
    state_col: str = "state",
    district_col: str = "district",
    pincode_col: str = "pincode",
) -> pd.DataFrame:
    """Clean a raw dataset and aggregate duplicates.

    Steps:
    - Strip whitespace from state and district.
    - Parse date column with dayfirst=True.
    - Group by (date, state, district, pincode) and sum numeric columns.
    """
    if df.empty:
        return df

    # Work on a copy to avoid mutating caller's DataFrame
    df = df.copy()

    # Strip text columns
    _strip_text_column(df, state_col)
    _strip_text_column(df, district_col)

    # Parse date column
    if date_col not in df.columns:
        raise KeyError(f"Expected date column '{date_col}' not found in DataFrame")
    df[date_col] = pd.to_datetime(df[date_col], dayfirst=True, errors="coerce")

    # Drop rows where key columns are missing or invalid dates
    df = df.dropna(subset=[date_col, state_col, district_col, pincode_col])

    # Ensure pincode is treated consistently (keep as is; assume numeric or string is fine)

    # Identify numeric columns to aggregate
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()

    # Remove key columns from numeric list if present
    for col in [date_col, state_col, district_col, pincode_col]:
        if col in numeric_cols:
            numeric_cols.remove(col)

    # If there are no numeric columns, just drop duplicates on keys
    if not numeric_cols:
        grouped = df.drop_duplicates(subset=[date_col, state_col, district_col, pincode_col])
    else:
        grouped = (
            df.groupby([date_col, state_col, district_col, pincode_col], dropna=False)[numeric_cols]
            .sum()
            .reset_index()
        )

    return grouped


def clean_enrolment(df: pd.DataFrame) -> pd.DataFrame:
    return clean_and_aggregate(df)


def clean_demographic(df: pd.DataFrame) -> pd.DataFrame:
    return clean_and_aggregate(df)


def clean_biometric(df: pd.DataFrame) -> pd.DataFrame:
    return clean_and_aggregate(df)

