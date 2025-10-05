from typing import Optional

import pandas as pd
from scipy.stats import stats

from src.infra.calculators.stat.base_stat_calculator import BaseStatCalculator, TestMethod, TestOutcome


class IndependentStatCalculator(BaseStatCalculator):
    """
    Класс для оценки статистических различий между двумя выборками
    с применением параметрического (t-критерий Стьюдента/Уэлча)
    и непараметрического (U-критерий Манна–Уитни) подхода.

    Методы:
        - run_test: выполняет выбранный тест и возвращает результат
          с p-value и размером эффекта.
        - calc_cohen_d: вычисляет поправленный размер эффекта Hedges' g
          (вариант d Коэна с поправкой на смещение).
        - calc_rank_biserial_signed: вычисляет знаковый rank-biserial коэффициент
          (эквивалент Cliff’s delta) для U-критерия.

    Основные источники:
        - Cohen, J. (1988). *Statistical Power Analysis for the Behavioral Sciences* (2nd ed.).
        - Hedges, L. V. (1981). Distribution theory for Glass's estimator of effect size
          and related estimators. *Journal of Educational Statistics*, 6(2), 107–128.
        - Cliff, N. (1993). Dominance statistics: Ordinal analyses to answer ordinal questions.
          *Psychological Bulletin*, 114(3), 494–509.
        - Kerby, D. S. (2014). The simple difference formula: An approach to teaching nonparametric correlation.
          *Comprehensive Psychology*, 3, 11.IT.3.1.
    """

    def prepare_data(self, x: pd.Series, y: pd.Series) -> tuple[pd.Series, pd.Series]:
        """
        Независимые выборки: NaN удаляем, индексы игнорируем.
        """
        x = x.dropna()
        y = y.dropna()
        x = x.reset_index(drop=True)
        y = y.reset_index(drop=True)
        return x, y

    def run_test(self, x: pd.Series, y: pd.Series, method: TestMethod) -> TestOutcome:
        if method == "t":
            stat, p = stats.ttest_ind(x, y, equal_var=False, nan_policy="omit")
            g = self.calc_cohen_d(x, y)

            return TestOutcome(
                stat=float(stat),
                p_value=float(p),
                effect_value=g,
                effect_kind="hedges_g"
            )

        else:
            res = stats.mannwhitneyu(x, y, alternative="two-sided", method="auto")
            stat, p = float(res.statistic), float(res.pvalue)
            r = self.calc_rank_biserial_signed(x, y)

            return TestOutcome(
                stat=stat,
                p_value=p,
                effect_value=r,
                effect_kind="rank_biserial_r"
            )

    def calc_cohen_d(self, x: pd.Series, y: pd.Series) -> Optional[float]:
        """
        Вычисляет размер эффекта Hedges’ g (исправленный d Коэна).

        Формула:
            d = (M_x - M_y) / SD_pooled
            g = d * J, где J = 1 - 3 / (4*df - 1)

        где:
            M_x, M_y — средние выборок,
            SD_pooled — объединённое стандартное отклонение,
            df = n_x + n_y - 2 (число степеней свободы).

        Применяется поправка Hedges’ J для уменьшения смещения при малых n.

        References:
            - Hedges, L. V. (1981).
            - Borenstein, M., Hedges, L. V., Higgins, J. P. T., & Rothstein, H. R. (2009).
              *Introduction to Meta-Analysis*. Wiley.
        """
        nx, ny = len(x), len(y)
        if nx < 2 or ny < 2:
            return None

        var_x = x.var(ddof=1)
        var_y = y.var(ddof=1)

        # Оба константны
        if var_x < 1e-12 and var_y < 1e-12:
            mean_diff = float(x.mean() - y.mean())
            return 0.0 if abs(mean_diff) < 1e-12 else None

        df = max(nx + ny - 2, 1)
        pooled_var = ((nx - 1) * var_x + (ny - 1) * var_y) / df
        if not np.isfinite(pooled_var) or pooled_var < 1e-12:
            return None

        pooled_std = float(np.sqrt(pooled_var))
        d = (x.mean() - y.mean()) / pooled_std

        # Поправка Hedges’ J
        J = 1.0 - 3.0 / (4.0 * df - 1.0) if df > 1 else 1.0
        return float(d) * J

    def calc_rank_biserial_signed(self, x: pd.Series, y: pd.Series) -> Optional[float]:
        """
        Вычисляет знаковый rank-biserial коэффициент (эквивалент Cliff’s delta).

        Формула:
            r = 2 * U_greater / (n * m) - 1

        где:
            U_greater — статистика Манна–Уитни при альтернативе "x > y",
            n, m — размеры выборок.

        Интерпретация:
            r = 1   → все значения x > y
            r = -1  → все значения y > x
            r = 0   → полное перекрытие распределений

        References:
            - Cliff, N. (1993).
            - Kerby, D. S. (2014).
        """
        n, m = len(x), len(y)
        if n == 0 or m == 0:
            return None
        U_greater = float(stats.mannwhitneyu(x, y, alternative="greater", method="auto").statistic)
        return 2.0 * (U_greater / (n * m)) - 1.0
