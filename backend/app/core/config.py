import os
from pathlib import Path
from pydantic import BaseModel


REPO_ROOT = Path(__file__).resolve().parents[3]
_DATA_FILE_ENV = os.environ.get("AADHAAR_DATA_FILE")
DEFAULT_DATA_FILE = Path(_DATA_FILE_ENV) if _DATA_FILE_ENV else (REPO_ROOT / "data" / "merged_aadhaar_data_sample.csv")


class Settings(BaseModel):
    """Application settings.

    For now we only manage the path to the merged Aadhaar CSV dataset.
    In a real deployment this could be populated from environment variables.
    """

    data_file: Path = DEFAULT_DATA_FILE


settings = Settings()

