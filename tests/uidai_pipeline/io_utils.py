import os
from pathlib import Path
from typing import List, Optional

import pandas as pd


def list_csv_files(directory: str) -> List[Path]:
    """Return a sorted list of CSV file paths in the given directory.

    Ignores non-CSV files. Returns an empty list if the directory has no CSVs.
    """
    dir_path = Path(directory)
    if not dir_path.exists():
        raise FileNotFoundError(f"Directory does not exist: {directory}")

    files = sorted(p for p in dir_path.iterdir() if p.is_file() and p.suffix.lower() == ".csv")
    return files


def load_and_concat_csvs(filepaths: List[Path], dtype: Optional[dict] = None) -> pd.DataFrame:
    """Load multiple CSVs and concatenate them into a single DataFrame.

    Returns an empty DataFrame if `filepaths` is empty.
    """
    if not filepaths:
        return pd.DataFrame()

    frames = [pd.read_csv(fp, dtype=dtype) for fp in filepaths]
    return pd.concat(frames, ignore_index=True)


def load_dataset_from_dir(directory: str, dtype: Optional[dict] = None) -> pd.DataFrame:
    """Convenience wrapper to load and concatenate all CSVs from a directory."""
    filepaths = list_csv_files(directory)
    return load_and_concat_csvs(filepaths, dtype=dtype)

