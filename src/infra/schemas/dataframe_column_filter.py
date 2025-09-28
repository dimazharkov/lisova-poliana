from typing import Optional, List

from pydantic import BaseModel, ConfigDict

from src.core.use_cases.dataframe_column_filter import Name, Idx


class DataFrameColumnFilterSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    columns: Optional[List[Name]] = None
    indexes: Optional[List[Idx]] = None
    keep: bool = True
