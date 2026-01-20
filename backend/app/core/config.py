import os
from pathlib import Path
from pydantic import BaseModel


REPO_ROOT = Path(__file__).resolve().parents[3]
_DATA_FILE_ENV = os.environ.get("AADHAAR_DATA_FILE")
# Default: Hugging Face dataset using hf:// protocol
# Can be overridden with AADHAAR_DATA_FILE environment variable (supports local paths, URLs, or hf:// protocol)
DEFAULT_DATA_FILE = (
    _DATA_FILE_ENV 
    if _DATA_FILE_ENV 
    else "hf://datasets/mrmarvelous/aadharclean/merged_aadhaar_data_sample.csv"
)


class Settings(BaseModel):
    """Application settings.

    For now we only manage the path to the merged Aadhaar CSV dataset.
    In a real deployment this could be populated from environment variables.
    Supports both local file paths and URLs.
    """

    data_file: str | Path = DEFAULT_DATA_FILE


settings = Settings()

