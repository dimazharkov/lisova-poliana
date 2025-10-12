import warnings
from typing import Optional

import numpy as np
import pandas as pd
from scipy import stats

from src.infra.calculators.stat.base_stat_calculator import BaseStatCalculator, TestMethod, TestOutcome
from src.infra.helpers.data_utils import aggregate_duplicates


class PairwiseStatCalculator(BaseStatCalculator):
    def prepare_data(self, x: pd.Series, y: pd.Series) -> tuple[pd.Series, pd.Series]:
        """
        Парные выборки: выравниваем по общему индексу-ключу пары.
        Требуем, чтобы индекс был «смысловым» (не RangeIndex).
        Дубликаты ключей в парном режиме не допускаем.
        """
        x = x.dropna()
        y = y.dropna()

        # защита от случайного RangeIndex: без ключа пара не определена
        if isinstance(x.index, pd.RangeIndex) or isinstance(y.index, pd.RangeIndex):
            raise ValueError(
                "PairwiseStatCalculator: ожидаются индексы-ключи пар (например, MultiIndex ['person','experiment'])."
            )

        if x.index.has_duplicates:
            dupes = x.index[x.index.duplicated()].unique().tolist()
            warnings.warn(
                f"PairwiseStatCalculator: найдены дубликаты ключей в индексе x: {dupes}"
            )
            x = aggregate_duplicates(x, agg_func_name="mean")

        if y.index.has_duplicates:
            dupes = y.index[y.index.duplicated()].unique().tolist()
            warnings.warn(
                f"PairwiseStatCalculator: найдены дубликаты ключей в индексе y: {dupes}"
            )
            y = aggregate_duplicates(y, agg_func_name="mean")

        common = x.index.intersection(y.index)
        if len(common) == 0:
            warnings.warn(
                f"PairwiseStatCalculator: нет общих индексов"
            )
            return x.iloc[0:0], y.iloc[0:0]

        x_aligned = x.loc[common]
        y_aligned = y.loc[common]

        # финальная страховка
        mask = x_aligned.notna() & y_aligned.notna()
        return x_aligned[mask], y_aligned[mask]


    def run_test(self, x: pd.Series, y: pd.Series, method: TestMethod) -> TestOutcome:
        if method == "t":
            stat, p = stats.ttest_rel(y, x, nan_policy="omit")
            d = self.calc_cohen_d(x, y)

            return TestOutcome(
                stat=float(stat),
                p_value=float(p),
                effect_value=d,
                effect_kind="cohen_d"
            )

        else:
            res = stats.wilcoxon(y, x, alternative="two-sided", zero_method="wilcox", method="auto")
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
        Вычисляет Cohen’s d для зависимых выборок (d_z) и безсмещённый аналог Hedges’ g_z.

        Формулы:
            d_z = mean(d) / sd(d),  где d = y - x
            g_z = d_z * J,  J = 1 - 3 / (4*(n-1) - 1)

        где:
            mean(d) — средняя разность пар,
            sd(d)   — стандартное отклонение разностей,
            n       — число пар.

        Особенности:
            - Если sd(d) ≈ 0 и mean(d) ≈ 0, возвращается 0.0 (нет эффекта).
            - Если sd(d) ≈ 0, но mean(d) ≠ 0, возвращается None (эффект неопределён).

        References:
            - Cohen, J. (1988).
            - Hedges, L. V. (1981).
            - Morris, S. B., & DeShon, R. P. (2002).
        """
        d = (y - x).dropna()
        n = len(d)
        if n < 2:
            return None

        mean_d = float(d.mean())
        sd = float(d.std(ddof=1))

        # обработка вырожденных случаев
        if not np.isfinite(sd) or sd < 1e-12:
            return 0.0 if abs(mean_d) < 1e-12 else None

        dz = mean_d / sd
        # Hedges’ correction для зависимых: df = n - 1
        df = n - 1
        j = 1.0 - 3.0 / (4.0 * df - 1.0) if df > 1 else 1.0
        gz = float(dz) * j
        return gz

    def calc_rank_biserial_signed(self, x: pd.Series, y: pd.Series) -> Optional[float]:
        """
        Вычисляет rank-biserial коэффициент (эквивалент Cliff’s δ)
        для парного теста Уилкоксона.

        Формулы:
            d = y - x
            Исключаются пары с d = 0 (zero_method="wilcox").
            Ранжируются |d|, затем:
                W_plus  = сумма рангов для d > 0
                W_minus = сумма рангов для d < 0
                R = n(n+1)/2
                r = (W_plus - W_minus) / R

        Интерпретация:
            r =  1 → все y > x
            r = -1 → все y < x
            r ≈ 0 → распределения максимально перекрываются

        References:
            - Cliff, N. (1993).
            - Kerby, D. S. (2014).
        """
        d = (y - x).replace(0, np.nan).dropna()
        n = len(d)
        if n == 0:
            return None

        ranks = stats.rankdata(np.abs(d))
        W_plus = float(ranks[d > 0].sum())
        W_minus = float(ranks[d < 0].sum())
        R = n * (n + 1) / 2.0
        return float((W_plus - W_minus) / R) if R > 0 else None