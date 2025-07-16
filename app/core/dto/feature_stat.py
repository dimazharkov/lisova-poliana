from dataclasses import dataclass
from typing import Optional

@dataclass
class FeatureStatsDTO:
    mean: Optional[float] = None
    median: Optional[float] = None
    std: Optional[float] = None
    min: Optional[float] = None
    max: Optional[float] = None
    variability: Optional[float] = None
    zero_percentage: Optional[float] = None
    IQR: Optional[float] = None
    outliers_count: Optional[int] = None
    outliers_percentage: Optional[float] = None
    skewness: Optional[float] = None
    non_zero_ratio: Optional[float] = None
    avg_zero_segment_length: Optional[float] = None
    num_zero_segments: Optional[int] = None
    avg_nonzero_segment_length: Optional[float] = None
    num_nonzero_segments: Optional[int] = None
    avg_measurement_interval: Optional[float] = None
    autocorrelation: Optional[float] = None
    exclusion_rate: float = 1.0
    conclusion: str = "Column is empty or contains only NaN values. Exclusion recommended."
