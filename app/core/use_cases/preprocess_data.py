import pandas as pd

from app.core.contracts.use_case_contract import UseCaseContract
from app.core.use_cases.clear_data import ClearDataUseCase
from app.core.use_cases.enrich_data import EnrichDataUseCase
from app.core.use_cases.normalize_data import NormalizeDataUseCase


class PreprocessDataUseCase(UseCaseContract):
    def __init__(
            self,
            clear_data_use_case: ClearDataUseCase,
            enrich_data_use_case: EnrichDataUseCase,
            normalize_data_use_case: NormalizeDataUseCase
    ):
        self.clear_data_use_case = clear_data_use_case
        self.enrich_data_use_case = enrich_data_use_case
        self.normalize_data_use_case = normalize_data_use_case

    def run(self, data: pd.DataFrame) -> pd.DataFrame:
        data = self.clear_data_use_case.run(data)
        data = self.enrich_data_use_case.run(data)
        data = self.normalize_data_use_case.run(data)
        return data