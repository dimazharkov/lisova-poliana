from dataclasses import dataclass
from typing import Optional, Union


@dataclass
class StatConclusion:
    score: Optional[float] = None
    category: Optional[str] = "not enough data"
    label: Optional[str] = "not enough data"