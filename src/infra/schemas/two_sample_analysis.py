from typing import AnyStr, Any

from pydantic import BaseModel, ConfigDict


class TwoSampleAnalysisSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    test_type: str
    test_method: str
    hue_field: str
    effect_field: str
    stratify_fields: list[str]
    index_fields: list[str]
    data_filter: dict[str, Any]
    experiment_config: dict[str, Any]
    target_folder: str
