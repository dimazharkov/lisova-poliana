from typing import TypeVar, runtime_checkable, Protocol

import pandas as pd

TIn  = TypeVar("TIn", contravariant=True)
TOut = TypeVar("TOut", covariant=True)

@runtime_checkable
class Filter(Protocol[TIn, TOut]):
    def filter(self, data: TIn) -> TOut: ...


class DataFrameFilterContract(Filter[pd.DataFrame, pd.DataFrame]):
    def filter(self, data: pd.DataFrame) -> pd.DataFrame: ...


class StringListFilterContract(Filter[list[str], list[str]]):
    def filter(self, data: list[str]) -> list[str]: ...
