import pandas as pd
import numpy as np
import operator
from typing import Any, Dict, List, Union, Optional

from src.core.contracts.use_case import DataUseCase


_OPS = {
    "==": operator.eq, "=": operator.eq, "!=": operator.ne,
    "<": operator.lt, "<=": operator.le, ">": operator.gt, ">=": operator.ge,
}

def _parse_inf(x: Any) -> float:
    if isinstance(x, str):
        xl = x.lower()
        if xl in ("inf", "+inf", "infinity"):
            return float("inf")
        if xl in ("-inf", "-infinity"):
            return float("-inf")
    return x

def _ensure_loc_idx(df: pd.DataFrame, loc: Union[int, str]) -> int:
    if isinstance(loc, int):
        return max(0, min(loc, df.shape[1]))
    if isinstance(loc, str):
        if loc not in df.columns:
            raise KeyError(f"Column '{loc}' not found")
        return df.columns.get_loc(loc) + 1
    raise TypeError("loc must be int or str")

def _spec_const(df: pd.DataFrame, spec: Dict[str, Any]) -> pd.Series:
    val = spec.get("value")
    return pd.Series(val, index=df.index)

def _spec_cut(df: pd.DataFrame, spec: Dict[str, Any]) -> pd.Series:
    src = spec["source"]
    if src not in df.columns:
        raise KeyError(f"source '{src}' not in df")
    bins = [_parse_inf(b) for b in spec["bins"]]
    labels = spec.get("labels")
    right = bool(spec.get("right", True))
    ser = pd.cut(df[src], bins=bins, labels=labels, right=right, include_lowest=not right)
    if labels is not None and all(isinstance(x, (int, np.integer)) for x in labels):
        return ser.astype("Int64")
    return ser.astype("category")

def _spec_select(df: pd.DataFrame, spec: Dict[str, Any]) -> pd.Series:
    default = spec.get("default", np.nan)
    out = pd.Series(default, index=df.index, dtype=object)
    for rule in spec.get("rules", []):
        conds = rule.get("when", [])
        if not conds:
            continue
        mask = pd.Series(True, index=df.index)
        for c in conds:
            col, op, val = c["col"], c["op"], c.get("value")
            if col not in df.columns:
                raise KeyError(f"select: column '{col}' not in df")
            if op not in _OPS:
                raise ValueError(f"Unsupported op '{op}'")
            mask &= _OPS[op](df[col], val)
        out = out.where(~mask, rule.get("then"))
    return out

def _build_series(df: pd.DataFrame, spec_or_value: Any) -> pd.Series:
    # Поддержка шортката: {"name": "...", "value": ...}
    if not isinstance(spec_or_value, dict) or "type" not in spec_or_value:
        return _spec_const(df, {"value": spec_or_value})
    t = spec_or_value.get("type")
    if t == "const":
        return _spec_const(df, spec_or_value)
    if t == "cut":
        return _spec_cut(df, spec_or_value)
    if t == "select":
        return _spec_select(df, spec_or_value)
    raise ValueError(f"Unknown spec.type '{t}'")


class AddColumnsUC(DataUseCase):
    """
    Применяет шаг:
      step_schema = {
        "loc": int | str,
        "columns": [
          {"name": "treatment", "spec": {...}}              # детальная спецификация
          {"name": "repeat",    "value": 0}                 # шорткат == const
        ]
      }
    """
    def __init__(
            self,
            loc: Union[int, str],
            columns: list[dict[str, Any]]
    ):
        self.loc = loc
        self.columns = columns


    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        idx = _ensure_loc_idx(out, self.loc)

        created: List[str] = []
        for col in self.columns:
            name = col["name"]
            spec_or_value = col.get("spec", col.get("value"))
            if spec_or_value is None:
                raise ValueError(f"Column '{name}' must have 'spec' or 'value'")
            ser = _build_series(out, spec_or_value).reindex(out.index)
            out[name] = ser
            created.append(name)

        # блок новых колонок вставляется с позиции idx
        cols = list(out.columns)
        for k in created:
            cols.remove(k)
        new_order = cols[:idx] + created + cols[idx:]
        return out[new_order]
