from __future__ import annotations

from typing import Sequence, Optional, Literal
from functools import reduce
import operator
import numpy as np
import pandas as pd

from src.core.contracts.use_case import DataUseCase


class CombineDatasetsUC(DataUseCase):
    """
    Склеивает список датафреймов в один.

    how: "intersection" — оставить только общие колонки (как у тебя сейчас),
         "union" — взять объединение колонок, недостающие заполнить fill_value.
    enforce_same_dtypes: выравнивать dtypes под первый датафрейм (best-effort).
    add_source_col: если задано имя, добавит колонку с индексом источника (0,1,...).
    fill_value: чем заполнять недостающие колонки в режиме "union".
    """
    def __init__(
        self,
        how: Literal["intersection", "union"] = "intersection",
        enforce_same_dtypes: bool = False,
        add_source_col: Optional[str] = None,
        fill_value: object = np.nan,
    ):
        self.how = how
        self.enforce_same_dtypes = enforce_same_dtypes
        self.add_source_col = add_source_col
        self.fill_value = fill_value

    def run(self, data: Sequence[pd.DataFrame]) -> pd.DataFrame:
        if not isinstance(data, (list, tuple)):
            raise TypeError("data must be a list/tuple of pandas.DataFrame")
        if len(data) == 0:
            raise ValueError("data is empty")
        if any(not isinstance(df, pd.DataFrame) for df in data):
            raise TypeError("all items in data must be pandas.DataFrame")
        if len(data) == 1:
            df0 = data[0].copy()
            if self.add_source_col:
                df0[self.add_source_col] = 0
            return df0

        # множество колонок
        if self.how == "intersection":
            common = list(reduce(operator.and_, (set(df.columns) for df in data)))
            # порядок берём из первого df
            cols = [c for c in data[0].columns if c in common]
            frames = [df[cols].copy() for df in data]
        else:  # union
            union = list(reduce(operator.or_, (set(df.columns) for df in data)))
            # порядок: колонки первого df, затем новые в порядке появления
            seen = set()
            cols = []
            for c in list(data[0].columns) + [c for df in data for c in df.columns]:
                if c not in seen and c in union:
                    seen.add(c)
                    cols.append(c)
            frames = []
            for df in data:
                f = df.reindex(columns=cols)
                # reindex уже проставит NaN для отсутствующих колонок; приведём к fill_value при необходимости
                if self.fill_value is not np.nan:
                    missing = [c for c in cols if c not in df.columns]
                    if missing:
                        f[missing] = self.fill_value
                frames.append(f)

        # выравнивание типов (опционально)
        if self.enforce_same_dtypes:
            ref_dtypes = frames[0].dtypes
            for i in range(1, len(frames)):
                for c, dt in ref_dtypes.items():
                    if c in frames[i].columns:
                        try:
                            frames[i][c] = frames[i][c].astype(dt)
                        except Exception:
                            # мягко пропускаем несовместимые приведения
                            pass

        # пометка источника (опционально)
        if self.add_source_col:
            for i, f in enumerate(frames):
                f[self.add_source_col] = i

        return pd.concat(frames, ignore_index=True)


# def run(self, data: list[pd.DataFrame]) -> pd.DataFrame:
#     common_cols_set = reduce(lambda x, y: x & y, (set(df.columns) for df in data))
#     first_df_cols = [col for col in data[0].columns if col in common_cols_set]
#     combined_df = pd.concat([df[first_df_cols] for df in data], ignore_index=True)    #
#     return combined_df

