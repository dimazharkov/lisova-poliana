import re
from typing import Optional, List

import pandas as pd

from app.core.contracts.dataframe_column_filter_contract import Name, Idx, DataFrameColumnFilterContract


class DataFrameColumnFilter(DataFrameColumnFilterContract):
    def __init__(
            self,
            columns: Optional[List[Name]] = None,
            indexes: Optional[List[Idx]] = None,
            keep: bool = True
    ):
        self.columns = columns
        self.indexes = indexes
        self.keep = keep

    def filter(
            self,
            df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        columns:
          - имена: "name", "h3", ...
          - диапазоны по именам: ("h5", "h15") -> h5..h15 (включительно), префикс должен совпадать
        indexes:
          - позиционные индексы: 0, 1, 3
          - диапазоны по индексам: (10, 20) -> 10..20 (включительно)

        keep=True  -> оставить только выбранные
        keep=False -> удалить выбранные
        """
        if not self.columns and not self.indexes:
            return df

        df = df.copy()
        names = set(self.expand_name_ranges(self.columns)) & set(df.columns)
        idx_names = {df.columns[i] for i in self.expand_index_ranges(self.indexes)}
        selected = names | idx_names

        if self.keep:
            result_cols = [c for c in df.columns if c in selected]
        else:
            result_cols = [c for c in df.columns if c not in selected]

        df = df.loc[:, result_cols]
        # print("filtered columns:")
        # print(df["h155"].unique())

        return df

    def expand_name_ranges(self, spec: Optional[List[Name]]) -> List[str]:
        if not spec:
            return []
        out: List[str] = []
        rx = re.compile(r"^([^\d]*)(\d+)$")  # префикс + числовой суффикс
        for item in spec:
            if isinstance(item, tuple) and len(item) == 2:
                a, b = item
                if not (isinstance(a, str) and isinstance(b, str)):
                    raise ValueError("Диапазон по именам должен быть строками, например ('h5','h15').")
                m1, m2 = rx.match(a), rx.match(b)
                if not (m1 and m2):
                    raise ValueError(f"Ожидалась пара вида ('h5','h15'), получено: {item}")
                if m1.group(1) != m2.group(1):
                    raise ValueError(f"Префиксы должны совпадать: {a} vs {b}")
                prefix = m1.group(1)
                start, end = int(m1.group(2)), int(m2.group(2))
                lo, hi = sorted((start, end))
                out.extend([f"{prefix}{i}" for i in range(lo, hi + 1)])
            else:
                if not isinstance(item, str):
                    raise ValueError(f"Имя колонки должно быть строкой: {item!r}")
                out.append(item)
        return out

    def expand_index_ranges(self, spec: Optional[List[Idx]]) -> List[int]:
        if not spec:
            return []
        out: List[int] = []
        for item in spec:
            if isinstance(item, int):
                out.append(item)
            elif isinstance(item, tuple) and len(item) == 2 and all(isinstance(x, int) for x in item):
                lo, hi = sorted(item)
                out.extend(list(range(lo, hi + 1)))
            else:
                raise ValueError(f"Неподдерживаемый формат индекса/диапазона: {item!r}")
        return out