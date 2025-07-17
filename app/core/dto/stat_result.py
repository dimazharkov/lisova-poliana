from dataclasses import dataclass
from typing import Literal, Union

from app.core.dto.stat_conclusion import StatConclusion


@dataclass
class StatResult:
    method: Literal["t", "u"]
    x_len: int
    y_len: int
    x_median: Union[float, str]
    y_median: Union[float, str]
    test_statistic: Union[float, str]
    p_value: Union[float, str]
    cohen_d: Union[float, str]
    effect_size: Union[float, str]
    relative_difference: Union[float, str]
    conclusion: Union[StatConclusion, str]