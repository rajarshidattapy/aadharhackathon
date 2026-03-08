from __future__ import annotations

import re
from typing import Dict

import pandas as pd


# Mapping of normalized keys (lowercased, trimmed, punctuation-stripped) to
# canonical state / UT names. Extend this over time as you see more variants.
_STATE_MAPPING: Dict[str, str] = {
    # Andhra Pradesh
    "andhra pradesh": "Andhra Pradesh",

    # West Bengal variants
    "west bengal": "West Bengal",
    "west  bengal": "West Bengal",
    "westbengal": "West Bengal",
    "west bangal": "West Bengal",
    "west bengli": "West Bengal",

    # Odisha / Orissa
    "odisha": "Odisha",
    "orissa": "Odisha",

    # Puducherry / Pondicherry
    "puducherry": "Puducherry",
    "pondicherry": "Puducherry",
}


def _normalize_key(value: str) -> str:
    """Normalize a raw state string into a lookup key.

    - strips leading/trailing whitespace
    - collapses multiple spaces
    - removes simple punctuation
    - lowercases
    """

    s = str(value).strip()
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"[.,'\"!?/\\;-]", "", s)
    return s.lower()


def normalize_state_name(value: str) -> str:
    """Normalize a single state value to a canonical representation.

    If the value is not in the mapping, we fall back to cleaned title case.
    """

    if pd.isna(value):
        return value  # keep NaN as NaN

    raw = str(value)
    key = _normalize_key(raw)

    if key in _STATE_MAPPING:
        return _STATE_MAPPING[key]

    # Default: tidy whitespace and use title case
    stripped = re.sub(r"\s+", " ", raw.strip())
    return stripped.title()


def normalize_state_column(df: pd.DataFrame, state_col: str = "state") -> pd.DataFrame:
    """Return a copy of df with the given state column normalized.

    Safe to call even if the column is missing.
    """

    if state_col not in df.columns:
        return df

    df = df.copy()
    df[state_col] = df[state_col].apply(normalize_state_name)
    return df

