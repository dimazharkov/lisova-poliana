from typing import Protocol

import pandas as pd


class UseCaseContract(Protocol):
    def run(self, data: pd.DataFrame) -> pd.DataFrame: ...