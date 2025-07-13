import pandas as pd

from app.utils.os_utils import load_df_from_disc, save_to_disc


class DataRepository:
    def __init__(self, source_path: str, target_path: str):
        self.data: pd.DataFrame = self._load_from_path(source_path)
        self.target_path = target_path

    def _load_from_path(self, source_path: str) -> pd.DataFrame:
        return load_df_from_disc(source_path)

    def all(self) -> pd.DataFrame:
        return self.data

    def save(self, data: dict | pd.DataFrame) -> None:
        save_to_disc(data, self.target_path)