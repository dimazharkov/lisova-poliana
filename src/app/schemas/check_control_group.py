from typing import Any

from pydantic import BaseModel, ConfigDict


class CheckControlGroupSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    test_type: str
    test_method: str
    hue_field: str
    effect_field: str
    experiment_config: dict[str, Any]
    target_folder: str