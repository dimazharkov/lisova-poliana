from typing import Any

from pydantic import BaseModel, ConfigDict


class ExtractDataFromRawSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    param_path: str
    data_section: str