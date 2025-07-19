from typing import Protocol

import pandas as pd


class RepositoryContract(Protocol):
    def all(self) -> pd.DataFrame | dict: ...
    def save(self, data: dict | pd.DataFrame) -> None: ...
