from dependency_injector import containers

from src.core.use_cases.add_columns import AddColumnsUC
from src.infra.schemas.add_columns import AddColumnsSchema


class AddColumnsFactory:
    Schema = AddColumnsSchema

    @staticmethod
    def create(container: containers.DeclarativeContainer, schema: AddColumnsSchema) -> AddColumnsUC:
        container.config.update(
            schema.model_dump()
        )

        return container.add_columns_uc()