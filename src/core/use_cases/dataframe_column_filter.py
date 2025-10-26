import re
from typing import Optional, List, Union, Tuple

import pandas as pd

from src.core.contracts.use_case import DataUseCase

Name = Union[str, Tuple[str, str], List[str]]
Idx  = Union[int, Tuple[int, int], List[int]]

class DataFrameColumnFilterUC(DataUseCase):
    """
    Filters a dataset by column names and/or index positions.

    columns:
      - explicit names: "name", "h3", ...
      - name ranges: ("h5", "h15") → columns h5..h15 (inclusive); textual prefix must match

    indexes:
      - positional indices: 0, 1, 3
      - index ranges: (10, 20) → positions 10..20 (inclusive)

    You may specify both columns and indexes at the same time; the result is the intersection
    of those filters. If both lists are empty (or omitted), the dataset is returned unchanged.

    keep=True  → keep only the selected columns/rows
    keep=False → drop the selected columns/rows
    """
    def __init__(
            self,
            columns: Optional[List[Name]] = None,
            indexes: Optional[List[Idx]] = None,
            keep: bool = True
    ):
        self.columns = columns
        self.indexes = indexes
        self.keep = keep

    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        if not self.columns and not self.indexes:
            return df

        df = df.copy()

        # имена из columns, отфильтрованные по реально существующим
        names = set(self.expand_name_ranges(self.columns)) & set(map(str, df.columns))

        # имена по позициям колонок (а НЕ строк!)
        idxs = self.expand_index_ranges(self.indexes)
        idxs = [i for i in idxs if 0 <= i < len(df.columns)]  # безопасная обрезка
        idx_names = {str(df.columns[i]) for i in idxs}

        # логика пересечения/объединения согласно докстрингу
        if self.columns and self.indexes:
            selected = names | idx_names
        else:
            selected = names or idx_names

        if self.keep:
            result_cols = [c for c in df.columns if str(c) in selected]
        else:
            result_cols = [c for c in df.columns if str(c) not in selected]

        return df.loc[:, result_cols]

    def expand_name_ranges(self, spec: Optional[List[Name]]) -> List[str]:
        if not spec:
            return []
        out: List[str] = []
        rx = re.compile(r"^([^\d]*)(\d+)$")
        for item in spec:
            if isinstance(item, (tuple, list)) and len(item) == 2:
                a, b = item
                if not (isinstance(a, str) and isinstance(b, str)):
                    raise ValueError("The name range must be strings, e.g. ['h5', 'h15'].")
                m1, m2 = rx.match(a), rx.match(b)
                if not (m1 and m2):
                    raise ValueError(f"Expected a pair like ['h5', 'h15']; got: {item}")
                if m1.group(1) != m2.group(1):
                    raise ValueError(f"Prefixes must match: {a} vs {b}")
                prefix = m1.group(1)
                lo, hi = sorted((int(m1.group(2)), int(m2.group(2))))
                out.extend([f"{prefix}{i}" for i in range(lo, hi + 1)])
            else:
                if not isinstance(item, str):
                    raise ValueError(f"Column name must be a string: {item!r}")
                out.append(item)
        return out

    def expand_index_ranges(self, spec: Optional[List[Idx]]) -> List[int]:
        if not spec:
            return []
        out: List[int] = []
        for item in spec:
            if isinstance(item, int):
                out.append(item)
            elif isinstance(item, (tuple, list)) and len(item) == 2 and all(isinstance(x, int) for x in item):
                lo, hi = sorted(item)
                out.extend(range(lo, hi + 1))
            else:
                raise ValueError(f"Unsupported index/range format: {item!r}")
        return out
