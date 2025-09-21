from dependency_injector import containers

from src.core.use_cases.read_json_from_disc import ReadJsonFromDiscUC
from src.infra.schemas.read_data_from_disc import ReadDataFromDiscSchema


class ReadJsonFromDiscFactory:
    Schema = ReadDataFromDiscSchema

    @staticmethod
    def create(container: containers.DeclarativeContainer, schema: ReadDataFromDiscSchema) -> ReadJsonFromDiscUC:
        container.config.update(
            schema.model_dump()
        )

        return container.read_json_from_disc_uc()