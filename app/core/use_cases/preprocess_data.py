import pandas as pd

from app.core.contracts.use_case_contract import UseCaseContract
from app.core.use_cases.clear_data import ClearDataUseCase
from app.core.use_cases.add_treatment_data import SetupRepeatAndTreatmentUseCase


class PreprocessDataUseCase(UseCaseContract):
    def __init__(
            self,
            clear_data_use_case: ClearDataUseCase,
            setup_repeat_and_treatment_use_case: SetupRepeatAndTreatmentUseCase,
    ):
        self.clear_data_use_case = clear_data_use_case
        self.setup_repeat_and_treatment_use_case = setup_repeat_and_treatment_use_case

    def run(self, data: pd.DataFrame) -> pd.DataFrame:
        data = self.clear_data_use_case.run(data)
        data = self.setup_repeat_and_treatment_use_case.run(data)
        return data