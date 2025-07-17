from typing import Optional, List

import pandas as pd
from matplotlib import pyplot as plt

from app.core.contracts.experiment_repository_contract import ExperimentRepositoryContract
from app.core.dto.experiment_result import ExperimentResultDTO
from app.utils.os_utils import save_to_disc, save_plot_to_disc, load_df_from_disc


class ExperimentRepository(ExperimentRepositoryContract):
    def __init__(
        self,
        source_paths: Optional[List[str]] = None,
        target_folder: Optional[str] = None,
        filters: Optional[dict] = None
    ) -> None:
        self.folder = target_folder
        self.filters = filters or {}
        self.data: Optional[pd.DataFrame] = self._load_and_merge(source_paths)

    def all(self) -> pd.DataFrame:
        return self.data

    def save(self, experiment_results: ExperimentResultDTO) -> None:
        if experiment_results.data:
            for key, data in experiment_results.data.items():
                self._save_data(key, data)
        if experiment_results.figures:
            for key, figure in experiment_results.figures.items():
                self._save_figure(key, figure)

    def _save_data(self, key: str, data: dict) -> None:
        path = f"{self.folder}/{key}.json" if self.folder else f"{key}.json"
        save_to_disc(data, path)

    def _save_figure(self, key: str, figure: plt.Figure) -> None:
        path = f"{self.folder}/{key}.png" if self.folder else f"{key}.png"
        save_plot_to_disc(figure, path)

    def _load_and_merge(self, paths: Optional[List[str]]) -> Optional[pd.DataFrame]:
        if not paths:
            return None

        dataframes = []
        for path in paths:
            df = load_df_from_disc(path)
            dataframes.append(df)

        combined = pd.concat(dataframes, ignore_index=True)
        return self._apply_filters(combined)

    def _apply_filters(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Применяет фильтры из self.filters к DataFrame.

        Поддерживаются два типа фильтров:
        - Простые сравнения на равенство: {column: value}
        - Операторы сравнения: {column: (operator, value)}, где operator — одна из строк: '>', '<', '>=', '<='

        :param data: Входной DataFrame, к которому нужно применить фильтрацию.
        :return: Новый DataFrame, отфильтрованный по заданным условиям.

        Примеры:
        --------
        self.filters = {
            "age": ('>', 40),
            "gender": "female",
            "pressure": ('<=', 130)
        }

        Тогда:
            _apply_filters(df)

        эквивалентен:

            df[(df["age"] > 40) & (df["gender"] == "female") & (df["pressure"] <= 130)]
        """
        if not self.filters:
            return data

        data = data.copy()
        for col, value in self.filters.items():
            if isinstance(value, tuple):  # например: ('>', 40)
                op, threshold = value
                if op == '>':
                    data = data[data[col] > threshold]
                elif op == '<':
                    data = data[data[col] < threshold]
                elif op == '<=':
                    data = data[data[col] <= threshold]
                elif op == '>=':
                    data = data[data[col] >= threshold]
            else:
                data = data[data[col] == value]
        return data


