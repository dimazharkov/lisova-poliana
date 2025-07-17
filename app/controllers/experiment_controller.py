from app.core.contracts.experiment_repository_contract import ExperimentRepositoryContract
from app.core.contracts.experiment_use_case_contract import ExperimentUseCaseContract


class ExperimentController:
    def __init__(self, experiment_repository: ExperimentRepositoryContract) -> None:
        self.experiment_repository = experiment_repository

    def run(self, use_case: ExperimentUseCaseContract) -> None:
        data = self.experiment_repository.all()
        experiment_results = use_case.run(
            data
        )
        self.experiment_repository.save(
            experiment_results
        )

