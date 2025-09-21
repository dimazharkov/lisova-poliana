from typing import Optional

from pydantic import BaseModel, ConfigDict


class WriteDataToDiscSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    source_path: Optional[str] = None
    target_path: str