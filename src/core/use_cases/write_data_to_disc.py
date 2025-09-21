from typing import Any

from src.core.contracts.file_repository import FileRepository
from src.core.contracts.use_case import DataUseCase


class WriteDataToDiscUC(DataUseCase):
    def __init__(self, data_repo: FileRepository):
        self.data_repo = data_repo

    def run(self, data: Any) -> Any:
        data = self.data_repo.write(data)
        return data