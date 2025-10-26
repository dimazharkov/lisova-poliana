import re
from typing import Optional, List, Union, Tuple

import pandas as pd

from src.core.contracts.filter import DataFrameFilterContract
from src.core.contracts.use_case import DataUseCase

class DataFrameDataFilterUC(DataUseCase):
    def __init__(self, df_filter: DataFrameFilterContract):
        self.df_filter = df_filter

    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        return self.df_filter.filter(
            data=df.copy()
        )