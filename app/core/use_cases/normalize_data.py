from sklearn.preprocessing import RobustScaler, MinMaxScaler
import pandas as pd

from app.core.contracts.column_filter_contract import ColumnListFilterContract
from app.core.contracts.use_case_contract import UseCaseContract


class NormalizeDataUseCase(UseCaseContract):
    def __init__(self, column_filter: ColumnListFilterContract):
        self.column_filter = column_filter

    def run(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.copy()

        target_columns = self.column_filter.filter(list(data.columns))

        robust_scaler = RobustScaler()
        robust_scaled = robust_scaler.fit_transform(data[target_columns])

        minmax_scaler = MinMaxScaler()
        final_scaled = minmax_scaler.fit_transform(robust_scaled)

        data[target_columns] = final_scaled

        return data