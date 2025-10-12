from typing import Any

from src.core.contracts.repository import JsonFileRepositoryContract
from src.core.contracts.use_case import NoInputUseCase


class ReadJsonFromDiscUC(NoInputUseCase):
    def __init__(self, data_repo: JsonFileRepositoryContract):
        self.data_repo = data_repo

    def run(self) -> Any:
        data = self.data_repo.read()
        return data