from typing import Optional, List, Dict, Callable
import numpy as np
import pandas as pd

from src.core.contracts.use_case import DataUseCase

DeltaFn = Callable[[float, float, float], float]

METHODS: Dict[str, DeltaFn] = {
    "logrel":    lambda v1, v2, eps: np.log1p((v2 - v1) / (v1 + eps)),
    "abslogrel": lambda v1, v2, eps: np.log1p(abs((v2 - v1) / (v1 + eps))),
    "logratio":  lambda v1, v2, eps: np.log((v2 + eps) / (v1 + eps)),
    "ratio":     lambda v1, v2, eps: (v2 + eps) / (v1 + eps),
    "diff":      lambda v1, v2, eps: (v2 - v1),
    "absdiff":   lambda v1, v2, eps: abs(v2 - v1),
    "relative":  lambda v1, v2, eps: (v2 - v1) / (v1 + eps),
}

class CalcDeltaUC(DataUseCase):
    def __init__(
        self,
        method: str,
        group_cols: List[str],
        sort_col: str,
        service_cols: Optional[List[str]] = None,
        eps: float = 1e-8,
    ):
        if method not in METHODS:
            raise ValueError(f"Unknown method '{method}'. Use one of {list(METHODS)}")
        self.delta = METHODS[method]
        self.group_cols = group_cols
        self.sort_col = sort_col
        self.service_cols = set(service_cols or [])
        self.eps = eps

    def run(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        block = set(self.group_cols) | self.service_cols | {self.sort_col}
        param_cols = [c for c in df.columns if c not in block]

        def compute(group: pd.DataFrame) -> Optional[pd.Series]:
            g = group.sort_values(self.sort_col, kind="stable")
            if len(g) != 2:
                return None
            r1, r2 = g.iloc[0], g.iloc[1]

            out = {k: r1[k] for k in self.group_cols}
            for col in param_cols:
                v1, v2 = r1[col], r2[col]
                if pd.notnull(v1) and pd.notnull(v2):
                    out[col] = float(self.delta(float(v1), float(v2), self.eps))
                else:
                    out[col] = np.nan
            return pd.Series(out, dtype="object")

        res = (
            df.groupby(self.group_cols, group_keys=False)
              .apply(compute)
              .reset_index(drop=True)
        )

        if not res.empty:
            res = res[self.group_cols + param_cols]

        return res
