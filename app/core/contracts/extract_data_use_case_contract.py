from typing import Protocol

import pandas as pd


class ExtractDataUseCaseContract(Protocol):
    def run(self, json_data: dict, param_aliases: list[str]) -> pd.DataFrame: ...