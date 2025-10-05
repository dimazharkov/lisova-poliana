from dependency_injector import containers

from src.app.schemas.add_personal_data import AddPersonalDataSchema
from src.app.use_cases.add_personal_data import AddPersonalDataUC


class AddPersonalDataFactory:
    Schema = AddPersonalDataSchema

    @staticmethod
    def create(container: containers.DeclarativeContainer, schema: AddPersonalDataSchema) -> AddPersonalDataUC:
        container.config.update(
            schema.model_dump()
        )

        return container.add_personal_data_uc()