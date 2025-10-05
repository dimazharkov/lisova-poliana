from dependency_injector import containers

from src.app.schemas.add_personal_indicators import AddPersonalIndicatorsSchema
from src.app.use_cases.add_personal_indicators import AddPersonalIndicatorsUC


class AddPersonalIndicatorsFactory:
    Schema = AddPersonalIndicatorsSchema

    @staticmethod
    def create(container: containers.DeclarativeContainer, schema: AddPersonalIndicatorsSchema) -> AddPersonalIndicatorsUC:
        container.config.update(
            schema.model_dump()
        )

        return container.add_personal_indicators_uc()