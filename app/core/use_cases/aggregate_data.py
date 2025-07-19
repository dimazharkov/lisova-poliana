from sklearn.preprocessing import RobustScaler, MinMaxScaler
import pandas as pd

from app.core.contracts.column_filter_contract import ColumnFilterContract
from app.core.contracts.use_case_contract import UseCaseContract


class AggregateDataUseCase(UseCaseContract):
    def __init__(self, column_filter: ColumnFilterContract):
        self.column_filter = column_filter

    def run(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.copy()

        target_columns = self.column_filter.filter(list(data.columns))

        data["median_effect"] = data[target_columns].median(axis=1)

        return data