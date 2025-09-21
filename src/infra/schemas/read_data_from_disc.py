from typing import Optional

from pydantic import BaseModel, ConfigDict


class ReadDataFromDiscSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    source_path: str
    target_path: Optional[str] = None