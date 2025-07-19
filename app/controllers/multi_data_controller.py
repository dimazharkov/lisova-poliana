from app.core.contracts.multi_repository_contract import MultiRepositoryContract
from app.core.contracts.use_case_contract import UseCaseContract


class MultiDataController:
    def __init__(self, repo: MultiRepositoryContract):
        self.repo = repo

    def run(self, use_case: UseCaseContract):
        datasets = self.repo.all()
        data = use_case.run(datasets)
        self.repo.save(data)
        print("done!")
