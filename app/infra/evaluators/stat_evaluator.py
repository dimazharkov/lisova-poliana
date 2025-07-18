from typing import Optional

import pandas as pd
import numpy as np
from scipy import stats

from app.core.contracts.stat_evaluator_contract import StatEvaluatorContract
from app.core.dto.stat_conclusion import StatConclusion
from app.core.dto.stat_result import StatResult


class StatEvaluator(StatEvaluatorContract):
    MIN_P_VALUE = 1e-4

    @staticmethod
    def evaluate(x: pd.Series, y: pd.Series, method: Optional[str] = None) -> StatResult:
        """
        Сравнивает два распределения с помощью t-теста или U-критерия Манна–Уитни и оценивает силу эффекта.

        Параметры:
            x (pd.Series): Первая выборка (сравниваемое распределение A).
            y (pd.Series): Вторая выборка (сравниваемое распределение B).
            method (Optional[str]): Метод сравнения:
                - 't' — Welch’s t-test (принимает неравные дисперсии),
                - 'u' — U-критерий Манна–Уитни (непараметрический),
                - None — автоматически выбирается по нормальности распределений (Shapiro–Wilk).

        Возвращает:
            StatResult: Объект с результатами сравнения:
                - длины выборок, медианы, значение теста, p-value;
                - показатель эффекта (Cohen’s d или rank-biserial correlation);
                - абсолютный и относительный сдвиг;
                - вывод о силе и направлении эффекта.

        Особенности:
            - Если выборки слишком малы (≤4 наблюдений), возвращается "not enough data".
            - Минимальное p-value ограничено (1e-4), чтобы избежать логарифмических аномалий.
            - Автоматический выбор метода работает до 5000 наблюдений на основе Shapiro–Wilk теста.
            - Для t-теста считается Cohen's d, для U-критерия — rank biserial r.
        """
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
                test_value="not enough data",
                p_value="not enough data",
                cohen_d="not enough data",
                rank_biserial_r="not enough data",
                effect_size="not enough data",
                relative_difference="not enough data",
                conclusion=StatConclusion()
            )

        x_median = x.median()
        y_median = y.median()
        effect_size = y_median - x_median
        relative_change = abs(effect_size) / (abs(x_median) + 1e-8)

        # Автовыбор метода
        if method is None:
            _, p_normal_x = stats.shapiro(x) if x_len < 5000 else (None, 1)
            _, p_normal_y = stats.shapiro(y) if y_len < 5000 else (None, 1)
            method = "t" if p_normal_x > 0.05 and p_normal_y > 0.05 else "u"

        if method == "t":
            stat, p_val = stats.ttest_ind(x, y, equal_var=False)
            cohen_d = StatEvaluator._calc_cohen_d(x, y)
            rank_biserial_r = "not applicable"
            conclusion = StatEvaluator._get_conclusion_t(p_val, cohen_d)
        elif method == "u":
            stat, p_val = stats.mannwhitneyu(x, y, alternative='two-sided')
            cohen_d = "not applicable"
            rank_biserial_r = 1 - (2 * stat) / (x_len * y_len)
            conclusion = StatEvaluator._get_conclusion_u(p_val, rank_biserial_r)

        else:
            raise ValueError("Unknown method. Use 't', 'u', or None.")

        safe_p_val = max(p_val, StatEvaluator.MIN_P_VALUE)

        return StatResult(
            method=method,
            x_len=x_len,
            y_len=y_len,
            x_median=round(x_median, 4),
            y_median=round(y_median, 4),
            test_value=round(stat, 4),
            p_value=round(safe_p_val, 4) if safe_p_val >= StatEvaluator.MIN_P_VALUE else f"< {StatEvaluator.MIN_P_VALUE:.0e}",
            cohen_d=round(cohen_d, 4) if isinstance(cohen_d, float) else cohen_d,
            rank_biserial_r=round(rank_biserial_r, 4) if isinstance(rank_biserial_r, float) else rank_biserial_r,
            effect_size=round(effect_size, 4),
            relative_difference=round(relative_change, 2),
            conclusion=conclusion
        )

    @staticmethod
    def _calc_cohen_d(x: pd.Series, y: pd.Series) -> float:
        nx, ny = len(x), len(y)
        if nx < 2 or ny < 2:
            return float("nan")

        var_x = x.std(ddof=1) ** 2
        var_y = y.std(ddof=1) ** 2
        pooled_var = ((nx - 1) * var_x + (ny - 1) * var_y) / (nx + ny - 2)
        pooled_std = np.sqrt(pooled_var)

        if pooled_std < 1e-8:
            return float("nan")

        return (x.mean() - y.mean()) / pooled_std

    @staticmethod
    def _get_conclusion_u(p_val: float, rank_biserial_r: float) -> StatConclusion:
        abs_r = abs(rank_biserial_r)

        if abs_r >= 0.5:
            r_strength = 1.0
        elif abs_r >= 0.3:
            r_strength = 0.8
        elif abs_r >= 0.1:
            r_strength = 0.4
        else:
            r_strength = 0.0

        if p_val < 0.01:
            p_strength = 1.0
        elif p_val < 0.05:
            p_strength = 0.6
        elif p_val < 0.1:
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

        direction = "positive" if rank_biserial_r > 0 else "negative"

        return StatConclusion(
            score=rounded_score,
            meaning=meaning,
            interpretation=f"{meaning.capitalize()} effect ({direction}), based on p-value and rank biserial correlation."
        )

    @staticmethod
    def _get_conclusion_t(p_value: float, cohen_d: float) -> StatConclusion:
        abs_d = abs(cohen_d)

        if abs_d >= 0.8:
            d_strength = 1.0
        elif abs_d >= 0.5:
            d_strength = 0.8
        elif abs_d >= 0.2:
            d_strength = 0.4
        else:
            d_strength = 0.0

        if p_value < 0.01:
            p_strength = 1.0
        elif p_value < 0.05:
            p_strength = 0.6
        elif p_value < 0.1:
            p_strength = 0.3
        else:
            p_strength = 0.0

        final_score = (d_strength + p_strength) / 2
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

        direction = "positive" if cohen_d > 0 else "negative"

        return StatConclusion(
            score=rounded_score,
            meaning=meaning,
            interpretation=f"{meaning.capitalize()} effect ({direction}), based on p-value and Cohen's d."
        )
