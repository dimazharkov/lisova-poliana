from typing import Optional

import pandas as pd

from src.core.contracts.file_repository import FileRepository
from src.infra.helpers.os_utils import save_to_disc, load_df_from_disc


class DataFileRepository(FileRepository[pd.DataFrame]):
    def __init__(self, source_path: Optional[str] = None, target_path: Optional[str] = None):
        self.data: Optional[pd.DataFrame] = self._load_from_path(source_path)
        self.target_path = target_path

    def _load_from_path(self, source_path: Optional[str]) -> Optional[pd.DataFrame]:
        return load_df_from_disc(source_path) if source_path else None

    def read(self) -> Optional[pd.DataFrame]:
        return self.data

    def write(self, data: pd.DataFrame) -> None:
        if self.target_path:
            save_to_disc(data, self.target_path)