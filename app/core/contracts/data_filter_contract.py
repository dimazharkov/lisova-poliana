from typing import Protocol

import pandas as pd


class DataFilterContract(Protocol):
    def filter(self, data: pd.DataFrame) -> pd.DataFrame: ...
