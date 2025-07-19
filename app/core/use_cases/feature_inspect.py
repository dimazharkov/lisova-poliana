import fnmatch
from dataclasses import asdict
from typing import List

import pandas as pd

from app.core.contracts.column_filter_contract import ColumnFilterContract
from app.core.contracts.repository_contract import RepositoryContract
from app.core.contracts.use_case_contract import UseCaseContract
from app.core.utils.stat_utils import column_statistics, clean_outliers


class FeatureInspectUseCase(UseCaseContract):
    def __init__(self, repository: RepositoryContract, column_filter: ColumnFilterContract) -> None:
        self.repository = repository
        self.column_filter = column_filter

    def run(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.copy()

        target_columns = self.column_filter.filter(list(data.columns))

        noizy_columns = []
        noizy_stat = {}
        for col in target_columns:
            cleaned_series = clean_outliers(data[col])
            data[col] = cleaned_series
            stat = column_statistics(cleaned_series)
            if stat.exclusion_rate > 0.6 or stat.zero_percentage > 90:
                noizy_columns.append(col)
                noizy_stat[col] = asdict(stat)

        self.repository.save(noizy_stat)

        data = data.drop(columns=noizy_columns)

        return data
