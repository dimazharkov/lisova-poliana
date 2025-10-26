from typing import Literal, Optional, Union

from pydantic import BaseModel, ConfigDict

FillType = Optional[Union[float, int, str, bool]]

class CombineDatasetsSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    how: Literal["intersection", "union"] = "intersection"
    enforce_same_dtypes: bool = False
    add_source_col: Optional[str] = None
    fill_value: FillType = None