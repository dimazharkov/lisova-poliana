from typing import Optional, Union, List

from pydantic import BaseModel, ConfigDict


class ReadDataFromDiscSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    source_path: Union[str, List[str]]
    target_path: Optional[str] = None