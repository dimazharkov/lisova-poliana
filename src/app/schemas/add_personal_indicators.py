from pydantic import BaseModel, ConfigDict


class AddPersonalIndicatorsSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    meta_path: str
    merge_column: str
    anchor_column: str