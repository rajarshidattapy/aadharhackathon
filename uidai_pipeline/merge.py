from typing import List

import pandas as pd

from .io_utils import load_dataset_from_dir
from .transform import KEY_COLS, clean_biometric, clean_demographic, clean_enrolment


def merge_datasets(
    enrolment_df: pd.DataFrame,
    demographic_df: pd.DataFrame,
    biometric_df: pd.DataFrame,
    how: str = "outer",
) -> pd.DataFrame:
    """Merge the three cleaned datasets on key columns using the specified join type."""

    merged = enrolment_df
    if not demographic_df.empty:
        merged = merged.merge(demographic_df, on=KEY_COLS, how=how, suffixes=("_enrol", "_demo"))
    if not biometric_df.empty:
        # Handle potential suffix collisions: if demographic was empty, enrolment suffix still applies
        suffixes = ("", "_bio") if demographic_df.empty else ("", "_bio")
        merged = merged.merge(biometric_df, on=KEY_COLS, how=how, suffixes=suffixes)
    return merged


def fill_missing_numerics(df: pd.DataFrame, fill_value: int | float = 0) -> pd.DataFrame:
    """Fill NaN values in numeric columns with the given fill value."""
    if df.empty:
        return df
    df = df.copy()
    numeric_cols = df.select_dtypes(include=["number"]).columns
    df[numeric_cols] = df[numeric_cols].fillna(fill_value)
    return df


def build_final_dataset(
    enrol_dir: str,
    demo_dir: str,
    bio_dir: str,
) -> pd.DataFrame:
    """Orchestrate the full pipeline: load, clean, merge, and fill NaNs."""
    enrol_raw = load_dataset_from_dir(enrol_dir)
    demo_raw = load_dataset_from_dir(demo_dir)
    bio_raw = load_dataset_from_dir(bio_dir)

    enrol_clean = clean_enrolment(enrol_raw) if not enrol_raw.empty else enrol_raw
    demo_clean = clean_demographic(demo_raw) if not demo_raw.empty else demo_raw
    bio_clean = clean_biometric(bio_raw) if not bio_raw.empty else bio_raw

    # Start with an empty DataFrame that has key columns, to support empty datasets gracefully
    if enrol_clean.empty and not (demo_clean.empty and bio_clean.empty):
        # Build a base from the first non-empty dataset
        base = demo_clean if not demo_clean.empty else bio_clean
        enrol_clean = base[KEY_COLS].drop_duplicates().copy()

    merged = merge_datasets(enrol_clean, demo_clean, bio_clean, how="outer")
    merged_filled = fill_missing_numerics(merged, fill_value=0)
    return merged_filled

