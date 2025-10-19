from dependency_injector import containers

from src.core.use_cases.combine_datasets import CombineDatasetsUC
from src.infra.schemas.combine_datasets import CombineDatasetsSchema


class CombineDatasetsFactory:
    Schema = CombineDatasetsSchema

    @staticmethod
    def create(container: containers.DeclarativeContainer, schema: CombineDatasetsSchema) -> CombineDatasetsUC:
        container.config.update(
            schema.model_dump()
        )

        return container.combine_datasets_uc()