from typing import Optional

from pydantic import BaseModel, ConfigDict


class CalcDeltaSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    method: str
    group_cols: list[str]
    sort_col: str
    service_cols: Optional[list[str]] = None