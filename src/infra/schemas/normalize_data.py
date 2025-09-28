from typing import Optional

from pydantic import BaseModel, ConfigDict


class NormalizeDataSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    include_patterns: list[str]
    exclude_fields: list[str]
    scallers: Optional[list[str]] = None