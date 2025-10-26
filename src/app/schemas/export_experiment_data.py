from pydantic import BaseModel, ConfigDict


class ExportExperimentDataSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    source_path: str
    target_path: str
    config_path: str