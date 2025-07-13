from typing import Protocol

import pandas as pd


class ExtractUseCaseContract(Protocol):
    def run(self, json_data: dict) -> dict | pd.DataFrame: ...