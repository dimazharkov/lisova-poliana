from dataclasses import dataclass
from typing import Optional, Union


@dataclass
class StatConclusion:
    score: Optional[float] = None
    meaning: Optional[str] = "not enough data"
    interpretation: Optional[str] = "not enough data"