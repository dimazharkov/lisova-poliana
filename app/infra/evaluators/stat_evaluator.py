from typing import Optional

import pandas as pd
import numpy as np
from scipy import stats

from app.core.dto.stat_conclusion import StatConclusion
from app.core.dto.stat_result import StatResult


class StatEvaluator:
    @staticmethod
    def evaluate(x: pd.Series, y: pd.Series, method: Optional[str] = None) -> StatResult:
        x = x.dropna()
        y = y.dropna()
        x_len, y_len = len(x), len(y)
        threshold = x_len > 4 and y_len > 4

        if not threshold:
            return StatResult(
                method=method if method else "u",
                x_len=x_len,
                y_len=y_len,
                x_median="not enough data",
                y_median="not enough data",
                test_statistic="not enough data",
                p_value="not enough data",
                cohen_d="not enough data",
                effect_size="not enough data",
                relative_difference="not enough data",
                conclusion="not enough data"
            )

        x_median = x.median()
        y_median = y.median()
        effect_size = y_median - x_median
        relative_change = abs(effect_size) / (abs(x_median) + 1e-8)
        cohen_d = StatEvaluator._calc_cohen_d(x, y)

        # Определяем метод, если не задан
        if method is None:
            _, p_normal_x = stats.shapiro(x) if x_len < 5000 else (None, 1)
            _, p_normal_y = stats.shapiro(y) if y_len < 5000 else (None, 1)
            method = "t" if p_normal_x > 0.05 and p_normal_y > 0.05 else "u"

        # Стат-тест
        if method == "t":
            stat, p_val = stats.ttest_ind(x, y, equal_var=False)
            conclusion = StatEvaluator._get_conclusion_u(stat, p_val, x_len, y_len)  # Можно заменить при желании
        elif method == "u":
            stat, p_val = stats.mannwhitneyu(x, y, alternative='two-sided')
            conclusion = StatEvaluator._get_conclusion_u(stat, p_val, x_len, y_len)
        else:
            raise ValueError("Unknown method. Use 't', 'u', or None.")

        return StatResult(
            method=method,
            x_len=x_len,
            y_len=y_len,
            x_median=round(x_median, 4),
            y_median=round(y_median, 4),
            test_statistic=round(stat, 4),
            p_value=round(p_val, 4),
            cohen_d=round(cohen_d, 4),
            effect_size=round(effect_size, 4),
            relative_difference=round(relative_change, 2),
            conclusion=conclusion
        )

    @staticmethod
    def _calc_cohen_d(x: pd.Series, y: pd.Series) -> float:
        nx, ny = len(x), len(y)
        if nx < 2 or ny < 2:
            return float("nan")
        pooled_std = np.sqrt(((nx - 1)*x.std()**2 + (ny - 1)*y.std()**2) / (nx + ny - 2))
        return (x.mean() - y.mean()) / pooled_std if pooled_std > 0 else float("nan")

    @staticmethod
    def _get_conclusion_u(u_value: float, p_value: float, n_x: int, n_y: int) -> StatConclusion:
        if n_x < 5 or n_y < 5:
            return StatConclusion(
                value=None,
                meaning="insufficient data",
                p_value=round(p_value, 4),
                u_value=round(u_value, 4),
                rank_biserial_r=None,
                interpretation="Too few samples for stable effect estimation."
            )

        r_value = 1 - (2 * u_value) / (n_x * n_y)
        abs_r = abs(r_value)

        # r_strength
        if abs_r >= 0.5:
            r_strength = 1.0
        elif abs_r >= 0.3:
            r_strength = 0.8
        elif abs_r >= 0.1:
            r_strength = 0.4
        else:
            r_strength = 0.0

        # p_strength
        if p_value < 0.01:
            p_strength = 1.0
        elif p_value < 0.05:
            p_strength = 0.6
        elif p_value < 0.1:
            p_strength = 0.3
        else:
            p_strength = 0.0

        final_score = (r_strength + p_strength) / 2
        rounded_score = round(final_score, 4)

        if rounded_score >= 0.9:
            meaning = "very strong"
        elif rounded_score >= 0.7:
            meaning = "strong"
        elif rounded_score >= 0.5:
            meaning = "moderate"
        elif rounded_score >= 0.2:
            meaning = "weak"
        else:
            meaning = "no significant change"

        direction = "positive" if r_value > 0 else "negative"

        return StatConclusion(
            value=rounded_score,
            meaning=meaning,
            p_value=round(p_value, 4),
            u_value=round(u_value, 4),
            rank_biserial_r=round(r_value, 4),
            interpretation=f"{meaning.capitalize()} effect ({direction}), based on p-value and rank biserial correlation."
        )
