from dependency_injector import containers

from src.core.use_cases.write_data_to_disc import WriteDataToDiscUC
from src.infra.schemas.write_data_to_disc import WriteDataToDiscSchema


class WriteDataToDiscFactory:
    Schema = WriteDataToDiscSchema

    @staticmethod
    def create(container: containers.DeclarativeContainer, schema: WriteDataToDiscSchema) -> WriteDataToDiscUC:
        container.config.update(
            schema.model_dump()
        )

        return container.write_data_to_disc_uc()