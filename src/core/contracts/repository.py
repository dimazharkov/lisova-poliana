from pathlib import Path
from typing import List, Union, Protocol, Optional, Any

import pandas as pd
from matplotlib import pyplot as plt

PathLike = Union[str, Path]

DFList = List[pd.DataFrame]
DFOrList = Union[pd.DataFrame, DFList]

class DataFileRepositoryContract(Protocol):
    def read(self) -> Optional[DFOrList]: ...
    def write(self, data: DFOrList) -> None: ...


DictOrList = Union[dict[str, Any], List[dict[str, Any]]]

class JsonFileRepositoryContract(Protocol):
    def read(self) -> Optional[DictOrList]: ...
    def write(self, data: DictOrList) -> None: ...


class ExperimentRepositoryContract(Protocol):
    def save(self, data: Optional[dict[str, Any]] = None, figures: Optional[dict[str, plt.Figure]] = None) -> None: ...