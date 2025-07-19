from typing import Optional

import pandas as pd

from app.core.contracts.repository_contract import RepositoryContract
from app.utils.os_utils import load_df_from_disc, save_to_disc


class DataRepository(RepositoryContract):
    def __init__(self, source_path: Optional[str] = None, target_path: Optional[str] = None):
        self.data: Optional[pd.DataFrame] = self._load_from_path(source_path)
        self.target_path = target_path

    def _load_from_path(self, source_path: Optional[str]) -> Optional[pd.DataFrame]:
        return load_df_from_disc(source_path) if source_path else None

    def all(self) -> Optional[pd.DataFrame]:
        return self.data

    def save(self, data: dict | pd.DataFrame) -> None:
        if self.target_path:
            save_to_disc(data, self.target_path)