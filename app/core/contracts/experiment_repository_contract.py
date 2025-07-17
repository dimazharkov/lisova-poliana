from typing import Protocol

import pandas as pd

from app.core.dto.experiment_result import ExperimentResultDTO


class ExperimentRepositoryContract(Protocol):
    def all(self) -> pd.DataFrame: ...
    def save(self, experiment_results: ExperimentResultDTO) -> None: ...