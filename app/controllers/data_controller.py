from app.core.contracts.repository_contract import RepositoryContract
from app.core.contracts.use_case_contract import UseCaseContract


class DataController:
    def __init__(self, repo: RepositoryContract):
        self.repo = repo

    def run(self, use_case: UseCaseContract):
        data = self.repo.all()
        data = use_case.run(data)
        self.repo.save(data)
        print("done!")


