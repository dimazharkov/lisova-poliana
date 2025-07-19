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
            if isinstance(value, tuple):  # например: ('>', 40)
                op, threshold = value
                if op == '>':
                    data = data[data[col] > threshold]
                elif op == '<':
                    data = data[data[col] < threshold]
                elif op == '<=':
                    data = data[data[col] <= threshold]
                elif op == '>=':
                    data = data[data[col] >= threshold]
            else:
                data = data[data[col] == value]
        return data
