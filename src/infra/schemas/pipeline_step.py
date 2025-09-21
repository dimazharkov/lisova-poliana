from typing import Any
from pydantic import BaseModel, ConfigDict


class PipelineStepSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    use_case: str
    step_schema: dict[str, Any]