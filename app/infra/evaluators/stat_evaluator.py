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
            interpretation_data = StatEvaluator._matrix_interpretation(p_val, cohen_d, method)

        elif method == "u":
            stat, p_val = stats.mannwhitneyu(x, y, alternative='two-sided')
            cohen_d = "not applicable"
            rank_biserial_r = 1 - (2 * stat) / (x_len * y_len)
            interpretation_data = StatEvaluator._matrix_interpretation(p_val, rank_biserial_r, method)
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
            conclusion=StatConclusion(
                score=interpretation_data["score"],
                meaning=interpretation_data["category"],
                interpretation=interpretation_data["label"]
            )
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
    def _matrix_interpretation(p_value: float, effect_strength: float, method: str) -> dict:
        """
        Возвращает интерпретацию статистической значимости и силы эффекта на основе матричной схемы,
        построенной по уровням p-value и размера эффекта (Cohen’s d или rank-biserial r).

        Эта функция использует:
        - Академически обоснованные пороги для оценки:
            - p-value: <0.01 (высокая значимость), <0.05 (умеренная), <0.1 (тенденция к значимости).
              См.: Fisher, R.A. (1925). Statistical Methods for Research Workers.
            - effect size:
                - Для t-теста (Cohen's d): 0.2 (малый), 0.5 (средний), 0.8 (большой).
                  См.: Cohen, J. (1988). Statistical Power Analysis for the Behavioral Sciences.
                - Для U-теста (rank-biserial r): 0.1 (малый), 0.3 (средний), 0.5 (большой).
                  См.: Fritz, C.O., Morris, P.E., & Richler, J.J. (2012). Effect size estimates.

        Возвращаемый словарь включает:
        - `score`: агрегированное значение от 0 до 1, отражающее уверенность и силу эффекта.
        - `category`: компактное текстовое описание ("strong", "moderate", "negligible").
        - `label`: развернутая интерпретация, полезная для отчётов и визуализаций.

        Матричная схема, сопоставляющая комбинации p-value и effect size с качественными оценками,
        является эвристическим решением, не имеющим единого универсального стандарта.
        """
        p_cuts = [0.01, 0.05, 0.1]
        if method == "t":
            e_cuts = [0.2, 0.5, 0.8]  # for Cohen's d
        else:
            e_cuts = [0.1, 0.3, 0.5]  # for rank biserial r

        p_level = sum([p_value < cut for cut in p_cuts])  # 0 to 3
        e_level = sum([abs(effect_strength) >= cut for cut in e_cuts])  # 0 to 3

        label_matrix = {
            (0, 0): "немає ефекту",
            (0, 1): "можливий слабкий ефект",
            (0, 2): "можливий ефект",
            (0, 3): "великий ефект, але невизначений",
            (1, 0): "не має практичного значення",
            (1, 1): "слабкий, малоймовірно значущий ефект",
            (1, 2): "потенційно важливий ефект",
            (1, 3): "перспективний, але з низькою впевненістю",
            (2, 0): "статистично значущий, але мізерний ефект",
            (2, 1): "слабкий, але надійний ефект",
            (2, 2): "помірний і надійний ефект",
            (2, 3): "сильний і надійний ефект",
            (3, 0): "висока значущість, але мізерний розмір ефекту",
            (3, 1): "високонадійний слабкий ефект",
            (3, 2): "стійкий помірний ефект",
            (3, 3): "сильний, високозначущий ефект",
        }
        # label_matrix = {
        #     (0, 0): "no effect",
        #     (0, 1): "possibly weak effect",
        #     (0, 2): "possible effect",
        #     (0, 3): "large effect, uncertain",
        #     (1, 0): "not meaningful",
        #     (1, 1): "weak, marginally significant",
        #     (1, 2): "potentially relevant",
        #     (1, 3): "promising, low certainty",
        #     (2, 0): "statistically significant, but negligible",
        #     (2, 1): "weak but reliable",
        #     (2, 2): "moderate and reliable",
        #     (2, 3): "strong and reliable",
        #     (3, 0): "highly significant, negligible size",
        #     (3, 1): "highly reliable weak effect",
        #     (3, 2): "robust moderate effect",
        #     (3, 3): "strong, highly significant",
        # }

        # score_matrix = {
        #     (3, 3): (1.0, "decisive"),
        #     (3, 2): (0.75, "strong"),
        #     (2, 3): (0.75, "strong"),
        #     (2, 2): (0.5, "moderate"),
        #     (3, 1): (0.5, "moderate"),
        #     (1, 3): (0.5, "moderate"),
        #     (2, 1): (0.5, "moderate"),
        #     (1, 2): (0.5, "moderate"),
        #     (3, 0): (0.0, "negligible"),
        #     (2, 0): (0.0, "negligible"),
        #     (1, 0): (0.0, "negligible"),
        #     (0, 3): (0.0, "negligible"),
        #     (0, 2): (0.0, "negligible"),
        #     (0, 1): (0.0, "negligible"),
        #     (0, 0): (0.0, "negligible"),
        # }

        score_matrix = {
            # 0.0
            (0, 0): (0.0, "none"),

            # 0.2
            (1, 0): (0.2, "weak"),
            (0, 1): (0.2, "weak"),
            (0, 2): (0.2, "weak"),
            (1, 1): (0.2, "weak"),
            (2, 0): (0.2, "weak"),

            # 0.4
            (1, 2): (0.4, "low"),
            (0, 3): (0.4, "low"),
            (3, 0): (0.4, "low"),
            (1, 3): (0.4, "low"),
            (2, 1): (0.4, "low"),

            # 0.6
            (3, 1): (0.6, "moderate"),
            (2, 2): (0.6, "moderate"),

            # 0.8
            (3, 2): (0.8, "strong"),
            (2, 3): (0.8, "strong"),

            # 1.0
            (3, 3): (1.0, "decisive"),
        }

        key = (p_level, e_level)
        score, category = score_matrix.get(key, (0.0, "negligible"))
        label = label_matrix.get(key, "no interpretation available")

        return {
            "score": score,
            "label": label,
            "category": category
        }

    @staticmethod
    def _bayesian_interpretation(
            x: pd.Series,
            y: pd.Series,
            rope: tuple = (-0.1, 0.1),
            n_samples: int = 10000
    ) -> dict:
        x_values = x.dropna().values
        y_values = y.dropna().values

        # Бутстрап-выборка с возвращением
        x_samples = np.random.choice(x_values, size=n_samples, replace=True)
        y_samples = np.random.choice(y_values, size=n_samples, replace=True)

        diffs = y_samples - x_samples

        # 95% HDI
        hdi_low, hdi_high = np.percentile(diffs, [2.5, 97.5])

        # Доля внутри ROPE
        in_rope = (diffs > rope[0]) & (diffs < rope[1])
        prop_in_rope = in_rope.mean()

        # Интерпретация
        if prop_in_rope > 0.95:
            score = 0.0
            category = "no effect"
            label = "≥95% posterior differences lie within ROPE — the effect is negligible."
        elif prop_in_rope < 0.05:
            score = 1.0
            category = "credible effect"
            label = "≤5% posterior differences lie within ROPE — strong and meaningful effect."
        else:
            score = 0.5
            category = "uncertain"
            label = (
                f"HDI = [{round(hdi_low, 4)}, {round(hdi_high, 4)}]; "
                f"{round(prop_in_rope * 100, 1)}% of differences lie within ROPE — inconclusive."
            )

        return {
            "score": score,
            "category": category,
            "label": label
        }
