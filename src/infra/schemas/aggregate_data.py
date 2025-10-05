from typing import Optional

from pydantic import BaseModel, ConfigDict


class AggregateDataSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    include_patterns: list[str]
    exclude_fields: list[str]
    agg_method: Optional[str] = None
    agg_field: Optional[str] = None