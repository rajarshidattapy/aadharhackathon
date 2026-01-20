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


def _convert_huggingface_url(url: str) -> str:
    """Convert Hugging Face blob URL to raw/resolve URL for direct download."""
    if "huggingface.co" in url and "/blob/" in url:
        return url.replace("/blob/", "/resolve/")
    return url


def _get_data_source(source: Union[str, Path]) -> Union[str, Path]:
    """Get the data source, converting Hugging Face URLs if needed."""
    if isinstance(source, str) and source.startswith("http"):
        return _convert_huggingface_url(source)
    return source


# Resolve repo root reliably from this file's location:
#   repo_root/backend/app/core/data_loader.py -> parents[3] == repo_root
REPO_ROOT = Path(__file__).resolve().parents[3]
# Data file is located at backend/app/data/merged_aadhaar_data_sample.csv
DATA_DIR = REPO_ROOT / "backend" / "app" / "data"
_MERGED_CSV_ENV = os.environ.get("AADHAAR_MERGED_CSV")
_MERGED_CSV_SOURCE = _MERGED_CSV_ENV if _MERGED_CSV_ENV else (
    "https://huggingface.co/datasets/mrmarvelous/aadharclean/resolve/main/merged_aadhaar_data_sample.csv"
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
    # pd.read_csv handles both local paths and URLs
    # For large files from URLs, use chunking to avoid memory issues
    try:
        if isinstance(MERGED_AADHAAR_CSV, str) and MERGED_AADHAAR_CSV.startswith("http"):
            # For URL downloads, read in chunks for large files (158MB)
            chunk_list = []
            for chunk in pd.read_csv(MERGED_AADHAAR_CSV, chunksize=50000):
                chunk_list.append(chunk)
            df = pd.concat(chunk_list, ignore_index=True)
        else:
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
    if isinstance(data_source, Path) or (isinstance(data_source, str) and not data_source.startswith("http")):
        path = Path(data_source)
        if not path.exists():
            raise FileNotFoundError(f"Data file not found at path: {path}")
        df = pd.read_csv(path)
    else:
        # It's a URL - read directly from URL with chunking for large files
        try:
            # For large URL files, read in chunks (158MB file)
            chunk_list = []
            for chunk in pd.read_csv(data_source, chunksize=50000):
                chunk_list.append(chunk)
            df = pd.concat(chunk_list, ignore_index=True)
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
