from pathlib import Path
from pydantic import BaseModel


class Settings(BaseModel):
    """Application settings.

    For now we only manage the path to the merged Aadhaar CSV dataset.
    In a real deployment this could be populated from environment variables.
    """

    data_file: Path = Path("data/merged_aadhaar_data_sample.csv")


settings = Settings()

