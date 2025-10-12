from typing import Any, Optional

from matplotlib import pyplot as plt

from src.core.contracts.repository import ExperimentRepositoryContract
from src.infra.helpers.os_utils import save_to_disc, save_plot_to_disc


class ExperimentRepository(ExperimentRepositoryContract):
    def __init__(self, target_folder: str):
        self.target_folder = target_folder

    def save(self, data: Optional[dict[str, Any]] = None, figures: Optional[dict[str, plt.Figure]] = None) -> None:
        if data:
            for key, data in data.items():
                self._save_data(key, data)
        if figures:
            for key, figure in figures.items():
                self._save_figure(key, figure)

    def _save_data(self, key: str, data: dict) -> None:
        path = f"{self.target_folder}/{key}.json" if self.target_folder else f"{key}.json"
        save_to_disc(data, path)

    def _save_figure(self, key: str, figure: plt.Figure) -> None:
        path = f"{self.target_folder}/{key}.png" if self.target_folder else f"{key}.png"
        save_plot_to_disc(figure, path)
