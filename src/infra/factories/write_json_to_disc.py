from dependency_injector import containers

from src.core.use_cases.write_json_to_disc import WriteJsonToDiscUC
from src.infra.schemas.write_data_to_disc import WriteDataToDiscSchema


class WriteJsonToDiscFactory:
    Schema = WriteDataToDiscSchema

    @staticmethod
    def create(container: containers.DeclarativeContainer, schema: WriteDataToDiscSchema) -> WriteJsonToDiscUC:
        container.config.update(
            schema.model_dump()
        )

        return container.write_json_to_disc_uc()