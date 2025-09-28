from pydantic import BaseModel, ConfigDict


class SetupRepeatAndTreatmentSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    treatment: int
