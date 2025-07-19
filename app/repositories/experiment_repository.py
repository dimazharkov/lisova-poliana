from typing import Optional, List

import pandas as pd
from matplotlib import pyplot as plt

from app.core.contracts.data_filter_contract import DataFilterContract
from app.core.contracts.experiment_repository_contract import ExperimentRepositoryContract
from app.core.dto.experiment_result import ExperimentResultDTO
from app.utils.os_utils import save_to_disc, save_plot_to_disc, load_df_from_disc


class ExperimentRepository(ExperimentRepositoryContract):
    def __init__(
            self,
            source_paths: Optional[List[str]] = None,
            target_folder: Optional[str] = None,
            data_filter: DataFilterContract = None
    ) -> None:
        self.target_folder = target_folder
        self.data_filter = data_filter
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
        path = f"{self.target_folder}/{key}.json" if self.target_folder else f"{key}.json"
        save_to_disc(data, path)

    def _save_figure(self, key: str, figure: plt.Figure) -> None:
        path = f"{self.target_folder}/{key}.png" if self.target_folder else f"{key}.png"
        save_plot_to_disc(figure, path)

    def _load_and_merge(self, paths: Optional[List[str]]) -> Optional[pd.DataFrame]:
        if not paths:
            return None

        dataframes = []
        for path in paths:
            df = load_df_from_disc(path)
            dataframes.append(df)

        combined = pd.concat(dataframes, ignore_index=True)
        filtered = self.data_filter.filter(combined)

        return filtered
