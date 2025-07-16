import numpy as np
import pandas
from scipy.stats import stats

from app.core.dto.feature_stat import FeatureStatsDTO

def get_outliner_boundaries(series: pandas.Series) -> tuple[float, float, float]:
    q1, q3 = np.percentile(series, [25, 75])
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    return lower, upper, iqr

def clean_outliers(series: pandas.Series) -> pandas.Series:
    series = series.dropna()
    if len(series) < 3:
        return series

    lower, upper, _ = get_outliner_boundaries(series)

    return series.where((series >= lower) & (series <= upper))

def column_statistics(column_data: pandas.Series):
    data = column_data.dropna()
    if len(data) <= 3:
        return FeatureStatsDTO()

    data_filled = column_data.fillna(0)

    mean_val = data.mean()
    median_val = data.median()

    std_val = data.std()
    min_val = data.min()
    max_val = data.max()

    # Variability
    variability = std_val / mean_val if mean_val != 0 else 0

    # IQR and outliers
    lower, upper, iqr = get_outliner_boundaries(data)
    outliers = ((data < lower) | (data > upper)).sum()
    outlier_ratio = outliers / len(data)

    skewness = calculate_skewness(data)

    # Percentage of zero values
    zero_percentage = (data == 0).sum() / len(data) * 100

    # Fraction of time with non-zero values
    non_zero_ratio = (data != 0).sum() / len(data)

    # Average length of zero segments and their number
    avg_zero_segment_length, num_zero_segments = count_segments(data_filled, zero=True)

    # Average length of non-zero segments and their number
    avg_nonzero_segment_length, num_nonzero_segments = count_segments(data_filled, zero=False)

    # Average measurement interval (difference between consecutive non-zero values)
    non_zero_indices = data[data != 0].index
    avg_measurement_interval = np.mean(np.diff(non_zero_indices)) if len(non_zero_indices) > 1 else np.nan

    # Autocorrelation (lag=1)
    if std_val == 0:
        autocorrelation = np.nan
    else:
        autocorrelation = data.autocorr(lag=1)

    # Statistical inference
    conclusion = []
    exclusion_rate = 0

    if outlier_ratio > 0.1:
        conclusion.append("Likely anomalies, consider robust normalization.")
    elif abs(skewness) > 1.0:
        conclusion.append("Highly skewed distribution, Min-Max may not be optimal.")
    else:
        conclusion.append("No significant outliers or skewness, Min-Max is applicable.")

    if avg_measurement_interval > 10:
        conclusion.append("High avg_measurement_interval suggests possible data gaps or irregular measurements.")

    # Evaluation for parameter exclusion
    if zero_percentage > 75:
        exclusion_rate += 0.3
        conclusion.append("High percentage of zero values.")
    if variability < 0.1:
        exclusion_rate += 0.2
        conclusion.append("Low variability, parameter does not change significantly.")
    if non_zero_ratio < 0.2:
        exclusion_rate += 0.2
        conclusion.append("Low non-zero ratio, parameter might be sparse.")
    if avg_zero_segment_length > avg_measurement_interval:
        exclusion_rate += 0.15
        conclusion.append("Zero segments are much longer than measurement interval, possibly discontinuous.")
    if not np.isnan(autocorrelation) and autocorrelation < 0.2:
        exclusion_rate += 0.15
        conclusion.append("Low autocorrelation, parameter is not continuous.")

    if exclusion_rate >= 0.75:
        conclusion.append("Exclusion recommended: parameter is not statistically significant and may negatively impact analysis.")

    return FeatureStatsDTO(
        mean=mean_val,
        median=median_val,
        std=std_val,
        min=min_val,
        max=max_val,
        variability=round(variability, 3),
        zero_percentage=round(zero_percentage, 2),
        IQR=iqr,
        outliers_count=int(outliers),
        outliers_percentage=round(outlier_ratio * 100, 2),
        skewness=round(skewness, 3) if not np.isnan(skewness) else None,
        non_zero_ratio=round(non_zero_ratio, 3),
        avg_zero_segment_length=round(avg_zero_segment_length, 3),
        num_zero_segments=num_zero_segments,
        avg_nonzero_segment_length=round(avg_nonzero_segment_length, 3),
        num_nonzero_segments=num_nonzero_segments,
        avg_measurement_interval=round(avg_measurement_interval, 3) if not np.isnan(avg_measurement_interval) else None,
        autocorrelation=round(autocorrelation, 3) if not np.isnan(autocorrelation) else None,
        exclusion_rate=round(exclusion_rate, 2),
        conclusion=" ".join(conclusion)
    )

def calculate_skewness(data):
    if len(data) < 3:  # Checking the minimum amount of data
        return np.nan

    std_val = data.std()

    if std_val == 0:  # Avoid division by 0
        return np.nan

    skewness = stats.skew(data, nan_policy='omit')

    return skewness

def count_segments(series, zero=True):
    binary_series = (series == 0).astype(int) if zero else (series != 0).astype(int)

    # If the entire series consists of only 1's (i.e. all non-zero)
    if binary_series.sum() == len(series):
        return len(series), 1  # Один длинный сегмент

    # If the entire row consists of only 0
    if binary_series.sum() == 0:
        return 0, 0

    changes = np.diff(binary_series.values)
    segment_starts = np.where(changes == 1)[0] + 1
    segment_ends = np.where(changes == -1)[0]

    # If the first element is 1, then the segment started from the very beginning
    if binary_series.iloc[0] == 1:
        segment_starts = np.insert(segment_starts, 0, 0)

    # If the last element is 1, then the segment ended at the very end
    if binary_series.iloc[-1] == 1:
        segment_ends = np.append(segment_ends, len(series) - 1)

    # Check that segment_starts and segment_ends have the same length
    if len(segment_starts) != len(segment_ends):
        return len(series), 1  # One long segment

    segment_lengths = segment_ends - segment_starts + 1
    segment_lengths = segment_lengths[segment_lengths > 0]  # Eliminate possible zero lengths

    avg_segment_length = np.mean(segment_lengths) if len(segment_lengths) > 0 else 0
    num_segments = len(segment_lengths)

    return avg_segment_length, num_segments
