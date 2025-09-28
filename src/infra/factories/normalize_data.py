from dependency_injector import containers

from src.core.use_cases.normalize_data import NormalizeDataUC
from src.infra.schemas.normalize_data import NormalizeDataSchema


class NormalizeDataFactory:
    Schema = NormalizeDataSchema

    @staticmethod
    def create(container: containers.DeclarativeContainer, schema: NormalizeDataSchema) -> NormalizeDataUC:
        container.config.update(
            schema.model_dump()
        )

        return container.normalize_data_uc()