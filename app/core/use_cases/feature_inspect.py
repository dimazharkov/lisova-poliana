import fnmatch
from dataclasses import asdict
from typing import List

import pandas as pd

from app.core.contracts.repository_contract import RepositoryContract
from app.core.contracts.use_case_contract import UseCaseContract
from app.core.utils.stat_utils import column_statistics, clean_outliers


class FeatureInspectUseCase(UseCaseContract):
    def __init__(
            self,
            repository: RepositoryContract,
            include_patterns: List[str] = None,
            exclude_fields: List[str] = None
    ) -> None:
        """
        :param include_patterns: список паттернов (масок) колонок, которые нужно анализировать.
               Примеры: ["h*", "vital_*", "bp_*"]
        :param exclude_fields: список точных названий колонок, которые нужно исключить из анализа.
               Примеры: ["h1_norm", "median_effect"]
        """
        super().__init__()
        self.repository = repository
        self.include_patterns = include_patterns
        self.exclude_fields = exclude_fields

    def run(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.copy()
        target_columns = self._filter_columns(data)

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

    def _filter_columns(self, df: pd.DataFrame) -> List[str]:
        all_columns = list(df.columns)

        # Если маски не заданы — берём все колонки
        if not self.include_patterns:
            matched = set(all_columns)
        else:
            matched = set()
            for pattern in self.include_patterns:
                matched.update(fnmatch.filter(all_columns, pattern))

        # Если исключения заданы — исключаем
        if self.exclude_fields:
            matched = [col for col in matched if col not in self.exclude_fields]
        else:
            matched = list(matched)

        return matched