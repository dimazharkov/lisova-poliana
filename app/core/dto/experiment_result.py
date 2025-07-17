from dataclasses import dataclass
from typing import Dict, Any
import matplotlib.pyplot as plt


@dataclass
class ExperimentResultDTO:
    data: Dict[str, Any]
    figures: Dict[str, plt.Figure]