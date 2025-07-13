from app.core.contracts.use_case_contract import UseCaseContract
from app.repositories.data_repository import DataRepository


class DataController:
    def __init__(self, repo: DataRepository):
        self.repo = repo

    def run(self, use_case: UseCaseContract):
        data = self.repo.all()
        data = use_case.run(data)
        self.repo.save(data)


