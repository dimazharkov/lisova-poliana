from typing import Protocol, Optional, List, Union, Tuple

import pandas as pd

Name = Union[str, Tuple[str, str]]
Idx  = Union[int, Tuple[int, int]]

class DataFrameColumnFilterContract(Protocol):
    def filter(self, df: pd.DataFrame) -> pd.DataFrame: ...