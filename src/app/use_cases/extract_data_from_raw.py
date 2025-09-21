from typing import Any

import pandas as pd

from src.core.contracts.file_repository import FileRepository
from src.core.contracts.use_case import DataUseCase


class ExtractDataFromRawUC(DataUseCase):
    def __init__(self, param_repo: FileRepository, data_section: str):
        self.param_repo = param_repo
        self.data_section = data_section

    def run(self, data: Any) -> Any:
        param_aliases = [f"h{i + 1}" for i in range(len(self.param_repo.read()))]
        raw_data = data[self.data_section]

        # Удаляем строки с индексами 0, 4, 5, 6, 10
        skip_rows = {0, 4, 5, 6, 10}
        data = [row for i, row in enumerate(raw_data) if i not in skip_rows]

        # Восстанавливаем порядок колонок из первой строки
        column_order = list(data[0].keys())  # col_1, col_2, ...
        data = pd.DataFrame(data)[column_order]

        # Шаг 1: добавляем искусственную колонку col_0 с будущими названиями колонок
        fixed_header = ["person", "sex", "dob", "category", "experiment", "experiment_date"] + param_aliases
        data.insert(0, "col_0", fixed_header)

        # Шаг 2: переставляем колонки так, чтобы col_0 шла первой
        full_columns = ["col_0"] + column_order
        data = data[full_columns]

        # Шаг 3: транспонируем
        data = data.T.reset_index(drop=True)

        # Шаг 4: первая строка — заголовки
        data.columns = data.iloc[0]
        data = data.drop(index=0).reset_index(drop=True)

        return data
