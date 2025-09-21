from dependency_injector import containers

from src.core.use_cases.read_data_from_disc import ReadDataFromDiscUC
from src.infra.schemas.read_data_from_disc import ReadDataFromDiscSchema


class ReadDataFromDiscFactory:
    Schema = ReadDataFromDiscSchema

    @staticmethod
    def create(container: containers.DeclarativeContainer, schema: ReadDataFromDiscSchema) -> ReadDataFromDiscUC:
        container.config.update(
            schema.model_dump()
        )

        return container.read_data_from_disc_uc()