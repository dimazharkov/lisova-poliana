from typing import List, Optional

import pandas as pd

from app.core.contracts.multi_repository_contract import MultiRepositoryContract
from app.repositories.data_repository import DataRepository
from app.utils.os_utils import save_to_disc


class MultiDataRepository(MultiRepositoryContract):
    def __init__(self, source_paths: List[str], target_path: Optional[str] = None):
        self.repositories = [DataRepository(source_path=path) for path in source_paths]
        self.target_path = target_path

    def all(self) -> List[pd.DataFrame]:
        """Возвращает список датафреймов, загруженных из каждого репозитория"""
        return [repo.all() for repo in self.repositories]

    def combined(self) -> pd.DataFrame:
        """Возвращает объединённый датафрейм из всех источников"""
        return pd.concat(self.all(), ignore_index=True)

    def repositories(self) -> List[DataRepository]:
        """Возвращает список объектов DataRepository"""
        return self.repositories

    def save(self, data: dict | pd.DataFrame) -> None:
        if self.target_path:
            save_to_disc(data, self.target_path)