import re
from typing import List, Optional

import pandas as pd

from app.core.contracts.data_filter_contract import DataFilterContract


class DataFilter(DataFilterContract):
    def __init__(self, filters: Optional[dict] = None):
        self.filters = filters

    def filter(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Применяет фильтры из self.filters к DataFrame.

        Поддерживаются два типа фильтров:
        - Простые сравнения на равенство: {column: value}
        - Операторы сравнения: {column: (operator, value)}, где operator — одна из строк: '>', '<', '>=', '<='

        :param data: Входной DataFrame, к которому нужно применить фильтрацию.
        :return: Новый DataFrame, отфильтрованный по заданным условиям.

        Примеры:
        --------
        self.filters = {
            "age": ('>', 40),
            "gender": "female",
            "pressure": ('<=', 130)
        }

        Тогда:
            _apply_filters(df)

        эквивалентен:

            df[(df["age"] > 40) & (df["gender"] == "female") & (df["pressure"] <= 130)]
        """
        if not self.filters:
            return data

        data = data.copy()

        for col, value in self.filters.items():
            # приводим колонку к числовому виду
            series = pd.to_numeric(data[col], errors="coerce")

            if isinstance(value, tuple):  # например: ('>', 40)
                op, threshold = value
                threshold = pd.to_numeric(pd.Series([threshold]), errors="coerce").iloc[0]

                if op == '>':
                    data = data[series > threshold]
                elif op == '<':
                    data = data[series < threshold]
                elif op == '<=':
                    data = data[series <= threshold]
                elif op == '>=':
                    data = data[series >= threshold]
            else:
                value = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
                data = data[series == value]

        return data
