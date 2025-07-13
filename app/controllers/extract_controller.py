from app.core.contracts.extract_data_use_case_contract import ExtractDataUseCaseContract
from app.core.contracts.extract_use_case_contract import ExtractUseCaseContract
from app.core.contracts.use_case_contract import UseCaseContract
from app.repositories.data_repository import DataRepository
from app.repositories.json_repository import JsonRepository


class ExtractController:
    def __init__(self, repo: JsonRepository):
        self.repo = repo

    def extract(self, use_case: ExtractUseCaseContract):
        json_data = self.repo.all()
        data = use_case.run(json_data)
        self.repo.save(data)

    def extract_data(self, use_case: ExtractDataUseCaseContract, params_repo: JsonRepository):
        json_data = self.repo.all()
        param_aliases = [f"h{i + 1}" for i in range(len(params_repo.all()))]
        data = use_case.run(json_data, param_aliases=param_aliases)
        self.repo.save(data)

