import numpy as np
import pandas as pd

from src.core.contracts.filter import StringListFilterContract
from src.core.contracts.use_case import DataUseCase


class AggregateDataUC(DataUseCase):
    def __init__(self, column_filter: StringListFilterContract, agg_method: str = "median", agg_field: str = "median_effect"):
        self.column_filter = column_filter
        self.agg_method = agg_method
        self.agg_field = agg_field

    def run(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()

        target_columns = self.column_filter.filter(list(data.columns))

        df[target_columns] = (
            df[target_columns]
            .apply(pd.to_numeric, errors="coerce")
            .astype("float64")
        )

        x = df[target_columns]

        if self.agg_method == "median":
            s = x.median(axis=1, skipna=True)
        elif self.agg_method == "mean":
            s = x.mean(axis=1, skipna=True)
        elif self.agg_method == "sum":
            s = x.sum(axis=1, skipna=True)
        elif self.agg_method == "min":
            s = x.min(axis=1, skipna=True)
        elif self.agg_method == "max":
            s = x.max(axis=1, skipna=True)
        elif self.agg_method.startswith("q"):  # e.g. "q90"
            try:
                q = float(self.agg_method[1:]) / 100.0
            except ValueError as e:
                raise ValueError(f"Invalid quantile shorthand {m!r}. Use e.g. 'q90'.") from e
            if not 0.0 <= q <= 1.0:
                raise ValueError(f"Quantile must be in [0, 1], got {q}.")
            s = x.quantile(q, axis=1, interpolation="linear")
        elif self.agg_method == "iqr":
            q = x.quantile([0.25, 0.75], axis=1)
            s = pd.Series(q.loc[0.75].values - q.loc[0.25].values, index=X.index)
        elif self.agg_method == "mad":
            med = x.median(axis=1)
            s = x.sub(med, axis=0).abs().median(axis=1)
        elif self.agg_method == "gmean":
            arr = x.to_numpy(copy=False)
            arr = np.where(arr > 0, arr, np.nan)  # геом. среднее требует x>0
            s = pd.Series(np.exp(np.nanmean(np.log(arr), axis=1)), index=x.index)
        elif self.agg_method == "hmean":
            arr = x.to_numpy(copy=False)
            arr = np.where(arr > 0, arr, np.nan)
            s = pd.Series(len(target_columns) / np.nansum(1.0 / arr, axis=1), index=X.index)
        elif self.agg_method == "trimmed_mean":
            alpha = float(getattr(self, "trim_alpha", 0.1))
            lo = x.quantile(alpha, axis=1)
            hi = x.quantile(1 - alpha, axis=1)
            s = x.clip(lower=lo, upper=hi, axis=0).mean(axis=1)
        elif self.agg_method == "wavg":
            weights = pd.Series(getattr(self, "weights", {}), dtype="float64").reindex(cols).fillna(0.0)
            denom = float(weights.sum())
            s = x.mul(weights, axis=1).sum(axis=1) / (denom if denom != 0 else np.nan)
            if denom == 0:
                # нет валидных весов — fallback на обычное среднее
                s = x.mean(axis=1, skipna=True)
        elif self.agg_method == "zmean":
            col_std = x.std(axis=0, ddof=0).replace(0.0, np.nan)
            z = (x - x.mean(axis=0)) / col_std
            s = z.mean(axis=1, skipna=True)
        else:
            raise ValueError(f"Unknown agg_method: {self.agg_method!r}")

        # df[self.agg_field] = s
        new_cols = pd.DataFrame({self.agg_field: s}, index=df.index)
        df = pd.concat([df, new_cols], axis=1)
        return df
