from pathlib import Path
from typing import Optional, Union, Sequence

from src.core.contracts.repository import JsonFileRepositoryContract, PathLike, DictOrList
from src.infra.helpers.os_utils import load_from_disc, save_to_disc


class JsonFileRepository(JsonFileRepositoryContract):
    def __init__(
        self,
        source_path: Optional[Union[PathLike, Sequence[PathLike]]] = None,
        target_path: Optional[Union[PathLike, Sequence[PathLike]]] = None,
    ):
        self._source_paths = self._normalize_paths(source_path)
        self._target_paths = self._normalize_paths(target_path)
        self.data: Optional[DictOrList] = self._load_from_paths(self._source_paths)

    def read(self) -> Optional[DictOrList]:
        return self.data

    def write(self, data: DictOrList) -> None:
        if self._target_paths is None:
            return  # писать некуда — молча игнорируем (или подними ValueError по вкусу)

        # одиночный путь назначения
        if len(self._target_paths) == 1:
            if isinstance(data, dict):
                save_to_disc(data, self._target_paths[0])
                return
            raise TypeError(
                "target_path is a single path, but data is a list of Dict. "
                "Provide a single Dict or a list of target paths."
            )

        # несколько путей назначения
        if isinstance(data, dict):
            raise TypeError(
                "target_path is a list of paths, but data is a single Dict. "
                "Provide a list[Dict] of the same length as target_path."
            )

        if len(data) != len(self._target_paths):
            raise ValueError(
                f"Length mismatch: data has {len(data)} Dicts, "
                f"target_path has {len(self._target_paths)} paths."
            )

        for d, path in zip(data, self._target_paths):
            if not isinstance(d, dict):
                raise TypeError("All items in data must be dict.")
            save_to_disc(d, path)

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
    def _load_from_paths(paths: Optional[list[str]]) -> Optional[DictOrList]:
        if paths is None:
            return None
        if len(paths) == 0:
            return []  # пустой список путей → пустой список DF
        if len(paths) == 1:
            return load_from_disc(paths[0])
        return [load_from_disc(p) for p in paths]



# class JsonFileRepository(JsonFileRepositoryContract):
#     def __init__(self, source_path: Optional[str] = None, target_path: Optional[str] = None):
#         self.data: Optional[dict[str, Any]] = self._load_from_path(source_path)
#         self.target_path = target_path
#
#     def _load_from_path(self, source_path: Optional[str] = None) -> Optional[dict[str, Any]]:
#         if not source_path:
#             return None
#         data = load_from_disc(source_path)
#         return data
#
#     def read(self) -> Optional[dict[str, Any]]:
#         return self.data
#
#     def write(self, data: dict[str, Any]) -> None:
#         if self.target_path:
#             save_to_disc(data, self.target_path)