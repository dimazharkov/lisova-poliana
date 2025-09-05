import pandas as pd


def aggregate_duplicates(s: pd.Series, agg_func_name: str = "mean") -> pd.Series:
    if s.index.has_duplicates:
        s = s.groupby(level=list(range(s.index.nlevels))).agg(agg_func_name)
    return s