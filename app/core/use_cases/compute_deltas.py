import numpy as np
import pandas as pd

from app.core.contracts.use_case_contract import UseCaseContract


class ComputeDeltasUseCase(UseCaseContract):
    def run(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.copy()

        group_fields = ["person", "sex", "dob", "age", "category", "experiment"]
        param_cols = [col for col in data.columns if col.startswith("h")]

        def compute_delta(group: pd.DataFrame) -> pd.Series:
            group_sorted = group.sort_values("experiment_date")

            if len(group_sorted) != 2:
                return None

            row1, row2 = group_sorted.iloc[0], group_sorted.iloc[1]

            result = {key: row1[key] for key in group_fields}
            result["date_before"] = row1["experiment_date"].date()
            result["date_after"] = row2["experiment_date"].date()

            abs_deltas = {}
            log_deltas = {}
            log_values_for_median = []

            for col in param_cols:
                val1 = row1[col]
                val2 = row2[col]

                abs_col = f"{col}_abs"
                abs_deltas[abs_col] = val2 - val1 if pd.notnull(val1) and pd.notnull(val2) else None

                log_col = f"{col}_log"
                if pd.notnull(val1) and pd.notnull(val2):
                    epsilon = 1e-8
                    log_val = np.log1p(np.abs((val2 - val1) / (val1 + epsilon)))
                    log_deltas[log_col] = log_val
                    log_values_for_median.append(log_val)
                else:
                    log_deltas[log_col] = None
                    log_values_for_median.append(np.nan)

            result.update(abs_deltas)
            result.update(log_deltas)

            if np.any(~np.isnan(log_values_for_median)):
                result["effect_median"] = np.nanmedian(log_values_for_median)
            else:
                result["effect_median"] = np.nan

            return pd.Series(result)

        data = (
            data.groupby(group_fields, group_keys=False)
            .apply(compute_delta)
            .dropna(how="all", subset=[f"{col}_abs" for col in param_cols])
            .reset_index(drop=True)
        )

        return data