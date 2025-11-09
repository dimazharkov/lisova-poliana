from typing import AnyStr, Any, Optional

from pydantic import BaseModel, ConfigDict


class TwoSampleAnalysisSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    test_type: str
    test_method: str
    hue_field: Optional[str] = None
    effect_field: str
    stratify_fields: Optional[list[str]] = None
    index_fields: Optional[list[str]] = None
    filter_config: dict[str, Any]
    experiment_config: dict[str, Any]
    target_folder: str
