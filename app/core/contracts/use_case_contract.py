from typing import Protocol, Union, List

import pandas as pd


class UseCaseContract(Protocol):
    def run(self, data: Union[pd.DataFrame, List[pd.DataFrame]]) -> pd.DataFrame: ...
    # def run(self, data: pd.DataFrame) -> pd.DataFrame: ...