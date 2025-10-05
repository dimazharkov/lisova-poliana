from dependency_injector import containers

from src.core.use_cases.aggregate_data import AggregateDataUC
from src.infra.schemas.aggregate_data import AggregateDataSchema


class AggregateDataFactory:
    Schema = AggregateDataSchema

    @staticmethod
    def create(container: containers.DeclarativeContainer, schema: AggregateDataSchema) -> AggregateDataUC:
        container.config.update(
            schema.model_dump()
        )

        return container.aggregate_data_uc()