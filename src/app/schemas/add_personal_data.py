from pydantic import BaseModel, ConfigDict


class AddPersonalDataSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    meta_path: str
    merge_column: str
    anchor_column: str