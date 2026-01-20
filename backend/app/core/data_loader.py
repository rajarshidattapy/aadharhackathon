from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import List, Union
import os

import pandas as pd

from backend.app.core.config import settings
from backend.app.utils.time_utils import normalize_date_column, add_month_column
from backend.app.utils.state_utils import normalize_state_column


REQUIRED_COLUMNS: List[str] = [
    "date",
    "state",
    "district",
    "pincode",
    "age_0_5",
    "age_5_17",
    "age_18_greater",
    "demo_age_5_17",
    "demo_age_17_",
    "bio_age_5_17",
    "bio_age_17_",
]


class DataValidationError(Exception):
    """Raised when the underlying data is missing required structure."""


def _validate_columns(df: pd.DataFrame) -> None:
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise DataValidationError(f"Dataset missing required columns: {missing}")


def _validate_non_empty(df: pd.DataFrame) -> None:
    if df.empty:
        raise DataValidationError("Dataset is empty after loading.")


def _convert_to_hf_protocol(url: str) -> str:
    """Convert Hugging Face URL to hf:// protocol format."""
    if "huggingface.co" in url:
        # Extract dataset path from URL
        # e.g., https://huggingface.co/datasets/mrmarvelous/aadharclean/resolve/main/merged_aadhaar_data_sample.csv
        # becomes: hf://datasets/mrmarvelous/aadharclean/merged_aadhaar_data_sample.csv
        if "/datasets/" in url:
            parts = url.split("/datasets/")
            if len(parts) > 1:
                dataset_path = parts[1].split("/resolve/")[0] if "/resolve/" in parts[1] else parts[1].split("/blob/")[0]
                filename = url.split("/")[-1]
                return f"hf://datasets/{dataset_path}/{filename}"
    return url


def _get_data_source(source: Union[str, Path]) -> Union[str, Path]:
    """Get the data source, converting Hugging Face URLs to hf:// protocol if needed."""
    if isinstance(source, str):
        if source.startswith("hf://"):
            return source
        elif source.startswith("http") and "huggingface.co" in source:
            return _convert_to_hf_protocol(source)
    return source


# Resolve repo root reliably from this file's location:
#   repo_root/backend/app/core/data_loader.py -> parents[3] == repo_root
REPO_ROOT = Path(__file__).resolve().parents[3]
# Data file is located at backend/app/data/merged_aadhaar_data_sample.csv
DATA_DIR = REPO_ROOT / "backend" / "app" / "data"
_MERGED_CSV_ENV = os.environ.get("AADHAAR_MERGED_CSV")
_MERGED_CSV_SOURCE = _MERGED_CSV_ENV if _MERGED_CSV_ENV else (
    "hf://datasets/mrmarvelous/aadharclean/merged_aadhaar_data_sample.csv"
)
MERGED_AADHAAR_CSV = _get_data_source(_MERGED_CSV_SOURCE)


@lru_cache(maxsize=1)
def get_merged_aadhaar_dataframe() -> pd.DataFrame:
    """
    Load and cache the merged Aadhaar analytics dataset.

    - Parses date with dayfirst=True, errors='coerce'
    - Drops invalid dates
    - Adds `month` column as YYYY-MM
    - Supports both local file paths and URLs (including Hugging Face datasets).
    """
    # pd.read_csv supports hf:// protocol for Hugging Face datasets
    # This is more efficient than downloading via HTTP
    try:
        df = pd.read_csv(MERGED_AADHAAR_CSV)
    except Exception as e:
        raise DataValidationError(f"Failed to load dataset from {MERGED_AADHAAR_CSV}: {str(e)}") from e

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")
        df = df[df["date"].notna()].copy()
        df["month"] = df["date"].dt.to_period("M").astype(str)

    # Ensure key numeric columns exist and are numeric (fill NaN with 0)
    numeric_cols = [
        "age_0_5",
        "age_5_17",
        "age_18_greater",
        "demo_age_5_17",
        "demo_age_17_",
        "bio_age_5_17",
        "bio_age_17_",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df


@lru_cache(maxsize=1)
def get_dataset() -> pd.DataFrame:
    """Load and cache the main Aadhaar dataset as a pandas DataFrame.

    - Uses an LRU cache so the CSV is read only once per process lifetime.
    - Validates required columns and non-empty data.
    - Parses the date column and adds a `month` column in YYYY-MM format.
    - Supports both local file paths and URLs (including Hugging Face datasets).
    """

    data_source = _get_data_source(settings.data_file)
    
    # Check if it's a local file path
    if isinstance(data_source, Path) or (isinstance(data_source, str) and not data_source.startswith(("http", "hf://"))):
        path = Path(data_source)
        if not path.exists():
            raise FileNotFoundError(f"Data file not found at path: {path}")
        df = pd.read_csv(path)
    else:
        # It's a URL or hf:// protocol - pd.read_csv handles both
        try:
            df = pd.read_csv(data_source)
        except Exception as e:
            raise DataValidationError(f"Failed to load dataset from {data_source}: {str(e)}") from e

    _validate_non_empty(df)
    _validate_columns(df)

    df = normalize_date_column(df, "date")
    _validate_non_empty(df.dropna(subset=["date"]))

    df = add_month_column(df, "date", "month")

    # Normalize state names so analytics always see canonical forms
    df = normalize_state_column(df, "state")

    # Ensure expected dtypes
    df["pincode"] = df["pincode"].astype(str).str.strip()

    numeric_cols = [
        "age_0_5",
        "age_5_17",
        "age_18_greater",
        "demo_age_5_17",
        "demo_age_17_",
        "bio_age_5_17",
        "bio_age_17_",
    ]
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce").fillna(0)

    return df
