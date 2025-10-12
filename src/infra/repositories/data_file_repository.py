from __future__ import annotations
from pathlib import Path
from typing import Optional, Union, Sequence, List
import pandas as pd

from src.core.contracts.repository import DataFileRepositoryContract, DFOrList, PathLike
from src.infra.helpers.os_utils import save_to_disc, load_df_from_disc

class DataFileRepository(DataFileRepositoryContract):
    """
    source_path: str | Path | list[str|Path] | None
      - str/Path  → read() вернёт DataFrame
      - list[...] → read() вернёт list[DataFrame]

    target_path: str | Path | list[str|Path] | None
      - str/Path                → write(DataFrame)
      - list[...]               → write(list[DataFrame]) с совпадающими размерами
      - при несоответствии типов/размеров — ошибка
    """
    def __init__(
        self,
        source_path: Optional[Union[PathLike, Sequence[PathLike]]] = None,
        target_path: Optional[Union[PathLike, Sequence[PathLike]]] = None,
    ):
        self._source_paths = self._normalize_paths(source_path)
        self._target_paths = self._normalize_paths(target_path)
        self.data: Optional[DFOrList] = self._load_from_paths(self._source_paths)

    def read(self) -> Optional[DFOrList]:
        return self.data

    def write(self, data: DFOrList) -> None:
        if self._target_paths is None:
            return  # писать некуда — молча игнорируем (или подними ValueError по вкусу)

        # одиночный путь назначения
        if len(self._target_paths) == 1:
            if isinstance(data, pd.DataFrame):
                save_to_disc(data, self._target_paths[0])
                return
            raise TypeError(
                "target_path is a single path, but data is a list of DataFrames. "
                "Provide a single DataFrame or a list of target paths."
            )

        # несколько путей назначения
        if isinstance(data, pd.DataFrame):
            raise TypeError(
                "target_path is a list of paths, but data is a single DataFrame. "
                "Provide a list[DataFrame] of the same length as target_path."
            )

        if len(data) != len(self._target_paths):
            raise ValueError(
                f"Length mismatch: data has {len(data)} frames, "
                f"target_path has {len(self._target_paths)} paths."
            )

        for df, path in zip(data, self._target_paths):
            if not isinstance(df, pd.DataFrame):
                raise TypeError("All items in data must be pandas.DataFrame.")
            save_to_disc(df, path)

    @staticmethod
    def _normalize_paths(p: Optional[Union[PathLike, Sequence[PathLike]]]) -> Optional[list[str]]:
        if p is None:
            return None
        if isinstance(p, (str, Path)):
            return [str(p)]
        # sequence of paths (but not string/bytes)
        if isinstance(p, Sequence) and not isinstance(p, (str, bytes)):
            return [str(x) for x in p]
        raise TypeError(f"Invalid path type: {type(p).__name__}")

    @staticmethod
    def _load_from_paths(paths: Optional[list[str]]) -> Optional[DFOrList]:
        if paths is None:
            return None
        if len(paths) == 0:
            return []  # пустой список путей → пустой список DF
        if len(paths) == 1:
            return load_df_from_disc(paths[0])
        return [load_df_from_disc(p) for p in paths]

# class DataFileRepository(FileRepository[pd.DataFrame]):
#     def __init__(self, source_path: Optional[str] = None, target_path: Optional[str] = None):
#         self.data: Optional[pd.DataFrame] = self._load_from_path(source_path)
#         self.target_path = target_path
#
#     def _load_from_path(self, source_path: Optional[str]) -> Optional[pd.DataFrame]:
#         return load_df_from_disc(source_path) if source_path else None
#
#     def read(self) -> Optional[pd.DataFrame]:
#         return self.data
#
#     def write(self, data: pd.DataFrame) -> None:
#         if self.target_path:
#             save_to_disc(data, self.target_path)
