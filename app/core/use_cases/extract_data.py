import pandas as pd

from app.core.contracts.extract_data_use_case_contract import ExtractDataUseCaseContract


class ExtractDataUseCase(ExtractDataUseCaseContract):
    def __init__(self, data_key: str) -> None:
        super().__init__()
        self.data_key = data_key

    def run(self, json_data: dict, param_aliases: list[str]) -> pd.DataFrame:
        raw_data = json_data[self.data_key]

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



