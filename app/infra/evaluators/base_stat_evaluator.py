from dataclasses import dataclass
from typing import Optional, Union, Literal

import pandas as pd
import numpy as np
from scipy import stats

from app.core.contracts.stat_evaluator_contract import StatEvaluatorContract
from app.core.dto.stat_conclusion import StatConclusion
from app.core.dto.stat_result import StatResult

EffectKind = Optional[Literal["cohen_d", "rank_biserial_r", "hedges_g"]]
TestMethod = Literal["t", "u"]

@dataclass
class TestOutcome:
    stat: float
    p_value: float
    effect_value: Optional[float] = None
    effect_kind: EffectKind = None

def round_or_none(v: Optional[float], digits: int = 4) -> Optional[float]:
    return round(float(v), digits) if isinstance(v, (float, np.floating)) and np.isfinite(v) else None

class BaseStatEvaluator(StatEvaluatorContract):
    def __init__(self):
        self.min_p_value = 1e-4

    def evaluate(self, x: pd.Series, y: pd.Series, method: Optional[str] = None) -> StatResult:
        x, y = self.prepare_data(x, y)
        x_len, y_len = len(x), len(y)
        print("^" * 100)
        if not (x_len > 4 and y_len > 4):
            return StatResult()
        print("*" * 100)
        x_med = float(np.median(x))
        y_med = float(np.median(y))
        effect_size = y_med - x_med

        use_method = self.choose_method(x_len, y_len, method)
        test_result = self.run_test(x, y, use_method)

        p_value = round(max(float(test_result.p_value), self.min_p_value), 4)
        conclusion = self.matrix_interpretation(
            p_value, test_result.effect_value, use_method
        )

        return StatResult(
            method=use_method,
            x_len=x_len,
            y_len=y_len,
            x_median=round_or_none(x_med),
            y_median=round_or_none(y_med),
            test_value=round_or_none(test_result.stat),
            p_value=p_value,
            effect_value=round_or_none(test_result.effect_value),
            effect_kind=test_result.effect_kind,
            effect_size=round_or_none(effect_size),
            conclusion=conclusion
        )

    def choose_method(self, x_len: int, y_len: int, method: Optional[str]) -> TestMethod:
        if method in ("t", "u"):
            return method
        # простая эвристика: при достаточных n — Welch t, иначе U
        return "t" if min(x_len, y_len) >= 20 else "u"

    def prepare_data(self, x: pd.Series, y: pd.Series) -> tuple[pd.Series, pd.Series]:
        raise NotImplementedError

    def run_test(self, x: pd.Series, y: pd.Series, method: TestMethod) -> TestOutcome:
        raise NotImplementedError

    def matrix_interpretation(self, p_value: float, effect_strength: float, method: str) -> StatConclusion:
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
        score, category = score_matrix.get(key, (0.0, "none"))
        label = label_matrix.get(key, "no interpretation available")

        return StatConclusion(
            score=score,
            category=category,
            label=label
        )