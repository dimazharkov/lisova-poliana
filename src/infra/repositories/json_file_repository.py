from typing import Any, Optional

from src.core.contracts.file_repository import FileRepository
from src.infra.helpers.os_utils import load_from_disc, save_to_disc


class JsonFileRepository(FileRepository[dict[str, Any]]):
    def __init__(self, source_path: Optional[str] = None, target_path: Optional[str] = None):
        self.data: Optional[dict[str, Any]] = self._load_from_path(source_path)
        self.target_path = target_path

    def _load_from_path(self, source_path: Optional[str] = None) -> Optional[dict[str, Any]]:
        if not source_path:
            return None
        data = load_from_disc(source_path)
        return data

    def read(self) -> Optional[dict[str, Any]]:
        return self.data

    def write(self, data: dict[str, Any]) -> None:
        if self.target_path:
            save_to_disc(data, self.target_path)