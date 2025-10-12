from dataclasses import dataclass
from typing import Optional, Literal

import pandas as pd

@dataclass
class StatConclusion:
    score: Optional[float] = None
    category: Optional[str] = "not enough data"
    label: Optional[str] = "not enough data"


@dataclass
class StatResult:
    method: Optional[Literal["t", "u"]] = None
    x_len: int = 0
    y_len: int = 0
    x_median: Optional[float] = None
    y_median: Optional[float] = None
    test_value: Optional[float] = None
    p_value: Optional[float] = None
    effect_value: Optional[float] = None
    effect_kind: Optional[str] = None
    effect_size: Optional[float] = None
    conclusion: Optional[StatConclusion]  = None


class StatCalculatorContract:
    @staticmethod
    def calculate(x: pd.Series, y: pd.Series, method: Optional[str] = None) -> StatResult: ...