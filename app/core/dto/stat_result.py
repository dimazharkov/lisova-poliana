from dataclasses import dataclass
from typing import Literal, Union, Optional

from proto import Field

from app.core.dto.stat_conclusion import StatConclusion


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