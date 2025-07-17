from typing import Protocol

import pandas as pd

from app.core.dto.experiment_result import ExperimentResultDTO


class ExperimentUseCaseContract(Protocol):
    def run(self, data: pd.DataFrame) -> ExperimentResultDTO: ...