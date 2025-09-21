from dependency_injector import containers

from src.app.schemas.extract_data_from_raw import ExtractDataFromRawSchema
from src.app.use_cases.extract_data_from_raw import ExtractDataFromRawUC


class ExtractDataFromRawFactory:
    Schema = ExtractDataFromRawSchema

    @staticmethod
    def create(container: containers.DeclarativeContainer, schema: ExtractDataFromRawSchema) -> ExtractDataFromRawUC:
        container.config.update(
            schema.model_dump()
        )

        return container.extract_data_from_raw_uc()