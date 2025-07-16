from typing import Optional

import pandas as pd

from app.core.contracts.repository_contract import RepositoryContract
from app.utils.os_utils import load_from_disc, save_to_disc


class JsonRepository(RepositoryContract):
    def __init__(self, source_path: Optional[str] = None, target_path: Optional[str] = None):
        self.data: Optional[dict] = self._load_from_path(source_path)
        self.target_path = target_path

    def _load_from_path(self, source_path: str) -> Optional[dict]:
        return load_from_disc(source_path) if source_path else None

    def all(self) -> dict:
        return self.data

    def save(self, data: dict | pd.DataFrame) -> None:
        if self.target_path:
            save_to_disc(data, self.target_path)