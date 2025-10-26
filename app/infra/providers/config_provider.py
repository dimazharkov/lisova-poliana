from pathlib import Path
from typing import Any, Optional, Union

from src.config import config
from app.core.contracts.config_provider_contract import ConfigProviderContract
from app.utils.os_utils import load_from_disc, save_to_disc


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


class ConfigProvider(ConfigProviderContract):
    def __init__(self, source_path: Union[str, Path], root: Optional[Path] = None) -> None:
        self.source_path = Path(source_path)
        self.root = root or config.config_path  # config.config_path должен быть заранее определён
        try:
            raw_config = load_from_disc(self.source_path, self.root)
            self._config = ConfigNode(raw_config)
        except FileNotFoundError:
            self._config = ConfigNode({})  # безопасное значение по умолчанию

    def __getattr__(self, item: str) -> Any:
        config = self.__dict__.get("_config", None)
        if config is None:
            raise AttributeError(f"'ConfigProvider' has no attribute '{item}' (no config loaded)")
        return getattr(config, item)

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        config = self.__dict__.get("_config", None)
        if config is None:
            return default
        return config.get(key, default)

    def save(self, data: dict):
        save_to_disc(data, self.source_path, self.root)

    def __repr__(self):
        return f"<ConfigProvider {getattr(self, '_config', None)}>"
