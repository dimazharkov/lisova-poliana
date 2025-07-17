from dataclasses import dataclass
from typing import Optional


@dataclass
class StatConclusion:
    value: Optional[float]
    meaning: str
    p_value: Optional[float]
    u_value: Optional[float]
    rank_biserial_r: Optional[float]
    interpretation: str