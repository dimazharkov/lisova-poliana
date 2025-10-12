from __future__ import annotations

from collections.abc import Mapping, MutableMapping
from typing import Any


def _wrap(value: Any) -> Any:
    if isinstance(value, Mapping):
        return DotDict(value)
    if isinstance(value, list):
        return [_wrap(v) for v in value]
    if isinstance(value, tuple):
        return tuple(_wrap(v) for v in value)
    return value

class DotDict(MutableMapping[str, Any]):
    """Dict с доступом по точке: obj.key.subkey.
    Списки/кортежи и вложенные dict’ы конвертируются рекурсивно.
    """
    __slots__ = ("_data",)

    def __init__(self, data: Mapping[str, Any] | None = None):
        object.__setattr__(self, "_data", {})
        if data:
            for k, v in data.items():
                self._data[k] = _wrap(v)

    # --- mapping API ---
    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._data[key] = _wrap(value)

    def __delitem__(self, key: str) -> None:
        del self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    # --- dot access ---
    def __getattr__(self, name: str) -> Any:
        try:
            return self._data[name]
        except KeyError as e:
            raise AttributeError(name) from e

    def __setattr__(self, name: str, value: Any) -> None:
        # защитим внутренние атрибуты
        if name == "_data":
            object.__setattr__(self, name, value)
        else:
            self._data[name] = _wrap(value)

    # удобства
    def to_dict(self) -> dict[str, Any]:
        def unwrap(v: Any) -> Any:
            if isinstance(v, DotDict):
                return {k: unwrap(x) for k, x in v.items()}
            if isinstance(v, list):
                return [unwrap(x) for x in v]
            if isinstance(v, tuple):
                return tuple(unwrap(x) for x in v)
            return v
        return {k: unwrap(v) for k, v in self._data.items()}

    def get_path(self, path: str, default: Any = None, sep: str = ".") -> Any:
        """Доступ по строковому пути: 'stratified.age_over_40.title'."""
        cur: Any = self
        for part in path.split(sep):
            try:
                cur = cur[part] if isinstance(cur, Mapping) else getattr(cur, part)
            except (KeyError, AttributeError):
                return default
        return cur