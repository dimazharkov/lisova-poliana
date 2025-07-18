from typing import Optional

import numpy as np
import pandas as pd

from app.core.contracts.use_case_contract import UseCaseContract


class ComputeDeltasUseCase(UseCaseContract):
    def run(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.copy()

        # гигиена: удаляем колонки, которые не нужны для расчета дельт
        data = data.drop(columns=[
            col for col in data.columns
            if col.endswith("_norm") or col == "median_effect" or col == "repeat"
        ])

        h1_index = data.columns.get_loc("h1")
        context_cols = list(data.columns[:h1_index])
        param_cols = [col for col in data.columns if col not in context_cols]
        group_cols = ["person", "sex", "dob", "age", "category", "experiment"]

        context_cols = [col for col in context_cols if col not in group_cols and col != "experiment_date"]

        def compute_delta(group: pd.DataFrame) -> Optional[pd.Series]:
            group_sorted = group.sort_values("experiment_date")

            if len(group_sorted) != 2:
                return None

            row1, row2 = group_sorted.iloc[0], group_sorted.iloc[1]

            result = {key: row1[key] for key in group_cols}
            result["date_before"] = row1["experiment_date"]
            result["date_after"] = row2["experiment_date"]

            for col in context_cols:
                result[col] = row1[col]

            abs_deltas = {}
            log_deltas = {}

            for col in param_cols:
                val1 = row1[col]
                val2 = row2[col]

                abs_col = f"{col}_abs"
                abs_deltas[abs_col] = val2 - val1 if pd.notnull(val1) and pd.notnull(val2) else None

                log_col = f"{col}_norm"
                if pd.notnull(val1) and pd.notnull(val2):
                    epsilon = 1e-8
                    log_val = np.log1p(np.abs((val2 - val1) / (val1 + epsilon)))
                    log_deltas[log_col] = log_val
                else:
                    log_deltas[log_col] = None

            result.update(abs_deltas)
            result.update(log_deltas)

            return pd.Series(result)

        data = (
            data.groupby(group_cols, group_keys=False)
            .apply(compute_delta)
            # .dropna(how="all", subset=[f"{col}_abs" for col in param_cols])
            # .dropna(how="all", subset=[f"{col}_norm" for col in param_cols])
            .reset_index(drop=True)
        )

        return data