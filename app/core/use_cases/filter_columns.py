import pandas as pd

from app.core.contracts.use_case_contract import UseCaseContract


class BuildDeltaUseCase(UseCaseContract):
    def run(self, data: pd.DataFrame) -> pd.DataFrame:
        ...