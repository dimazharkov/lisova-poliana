from typing import Optional

import numpy as np
import pandas as pd

from app.core.contracts.column_filter_contract import ColumnFilterContract
from app.core.contracts.use_case_contract import UseCaseContract


class BuildDeltaUseCase(UseCaseContract):
    def run(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.copy()
        data = data.drop(columns=["repeat"])

        group_cols = ["person", "sex", "dob", "age", "category", "experiment", "treatment"]
        param_cols = [col for col in data.columns if col not in group_cols]

        def compute_delta(group: pd.DataFrame) -> Optional[pd.Series]:
            group_sorted = group.sort_values("experiment_date")

            if len(group_sorted) != 2:
                return None

            row1, row2 = group_sorted.iloc[0], group_sorted.iloc[1]

            result = {key: row1[key] for key in group_cols}
            result["date_before"] = row1["experiment_date"]
            result["date_after"] = row2["experiment_date"]

            log_deltas = {}

            for col in param_cols:
                val1 = row1[col]
                val2 = row2[col]

                if pd.notnull(val1) and pd.notnull(val2):
                    epsilon = 1e-8
                    log_val = np.log1p(np.abs((val2 - val1) / (val1 + epsilon)))
                    log_deltas[col] = log_val
                else:
                    log_deltas[col] = None

            result.update(log_deltas)

            return pd.Series(result)

        data = (
            data.groupby(group_cols, group_keys=False)
            .apply(compute_delta)
            .reset_index(drop=True)
        )

        return data