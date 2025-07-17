from typing import Optional

import pandas as pd

from app.core.dto.stat_result import StatResult


class StatEvaluatorContract:
    @staticmethod
    def evaluate(x: pd.Series, y: pd.Series, method: Optional[str] = None) -> StatResult: ...
