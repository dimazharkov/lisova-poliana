from typing import Any

from src.core.contracts.repository import DataFileRepositoryContract
from src.core.contracts.use_case import DataUseCase


class WriteDataToDiscUC(DataUseCase):
    def __init__(self, data_repo: DataFileRepositoryContract):
        self.data_repo = data_repo

    def run(self, data: Any) -> Any:
        data = self.data_repo.write(data)
        return data