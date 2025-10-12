from __future__ import annotations
from typing import Any, Mapping, Sequence, Tuple
import pandas as pd

from src.core.contracts.filter import DataFrameFilterContract


class DataFrameFilter(DataFrameFilterContract):
    """
    Filters a DataFrame by a dict-based spec.

    filter_config format:
      - {"col": value}                  -> keep rows where df["col"] == value
      - {"col": [v1, v2, ...]}          -> keep rows where df["col"].isin([...])
      - {"col": (low, high)}            -> inclusive range:
           (a, b)     →  a <= x <= b
           (None, b)  →        x <= b
           (a, None)  →  a <= x
      Notes:
        * All column filters are combined with AND.
        * For range filters, the column is coerced to numeric; non-numeric/NaN values
          do not match the range predicate.
        * If a list is empty, or a tuple is not length-2, a ValueError is raised.
        * If a value is None (scalar), it matches NaNs in that column.

    Examples:
        {"experiment": 3}
        {"experiment": [3, 5]}
        {"experiment": 3, "h1": (0.15, 0.56)}
    """

    def __init__(self, filter_config: Mapping[str, Any]) -> None:
        self.filter_config = dict(filter_config or {})

    def filter(self, df: pd.DataFrame) -> pd.DataFrame:
        # print("type(df) = ", type(df))
        if not self.filter_config:
            return df  # nothing to filter

        mask = pd.Series(True, index=df.index)
        for col, rule in self.filter_config.items():
            if col not in df.columns:
                raise KeyError(f"Column not found: {col!r}")

            col_mask = self._make_mask(df[col], rule)
            mask &= col_mask

        return df.loc[mask]

    def _make_mask(self, s: pd.Series, rule: Any) -> pd.Series:
        # scalar None → select NaNs
        if rule is None:
            return s.isna()

        # range: tuple of (low, high)
        if isinstance(rule, tuple) and len(rule) == 2:
            low, high = rule
            sn = pd.to_numeric(s, errors="coerce")
            m = sn.notna()
            if low is not None:
                m &= sn >= low
            if high is not None:
                m &= sn <= high
            return m

        # discrete set: list/tuple/set of values (tuple here is NOT length-2)
        if isinstance(rule, (list, set, tuple)):
            # tuple length==2 already handled above
            vals = list(rule)
            if len(vals) == 0:
                raise ValueError("Empty list/set provided for filter; nothing can match.")
            return s.isin(vals)

        # scalar value
        return s == rule
