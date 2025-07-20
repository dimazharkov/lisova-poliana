from pathlib import Path
from typing import Any, Optional

from app.config import config
from app.utils.os_utils import load_from_disc


class ConfigNode:
    def __init__(self, config_dict: dict):
        self._dict = {}
        for key, value in config_dict.items():
            if isinstance(value, dict):
                self._dict[key] = ConfigNode(value)
            else:
                self._dict[key] = value

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        return self._dict.get(key, default)

    def __getitem__(self, item):
        return self._dict[item]

    def __getattr__(self, item):
        try:
            return self._dict[item]
        except KeyError:
            raise AttributeError(f"'ConfigNode' has no attribute '{item}'")

    def __iter__(self):
        return iter(self._dict)

    def __len__(self):
        return len(self._dict)

    def __contains__(self, item):
        return item in self._dict

    def __repr__(self):
        return f"<ConfigNode {self._dict}>"

    def as_dict(self) -> dict:
        result = {}
        for key, value in self._dict.items():
            if isinstance(value, ConfigNode):
                result[key] = value.as_dict()
            else:
                result[key] = value
        return result


class ConfigProvider:
    def __init__(self, source_path: str | Path, root: Optional[Path] = None) -> None:
        root = root or config.config_path
        raw_config = load_from_disc(source_path, root)
        self._config = ConfigNode(raw_config)

    def __getattr__(self, item: str) -> Any:
        return getattr(self._config, item)

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        return getattr(self._config, key, default)

    def __repr__(self):
        return f"<ExperimentConfigurator {self._config}>"
