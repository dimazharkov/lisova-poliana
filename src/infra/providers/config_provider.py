from pathlib import Path
from typing import Optional, Any, Union

from src.config import config
from src.core.contracts.config_provider import ConfigProviderContract
from src.infra.helpers.os_utils import load_from_disc, save_to_disc


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
        cfg = self.__dict__.get("_config", None)
        if cfg is None:
            return default

        if "." not in key:
            return cfg.get(key, default)

        node = cfg
        for part in key.split("."):
            if isinstance(node, ConfigNode):
                if part in node:
                    node = node[part]
                else:
                    return default
            else:
                return default

        return node

    def save(self, data: dict):
        save_to_disc(data, self.source_path, self.root)

    def as_dict(self) -> dict:
        cfg = self.__dict__.get("_config", None)
        if isinstance(cfg, ConfigNode):
            return cfg.as_dict()
        return {}

    def __repr__(self):
        return f"<ConfigProvider {getattr(self, '_config', None)}>"
