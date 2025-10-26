from typing import Any

from pydantic import BaseModel, ConfigDict


class DataFrameDataFilterSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    filter_config: dict[str, Any]