from dependency_injector import containers

from src.app.schemas.check_control_group import CheckControlGroupSchema
from src.app.use_cases.check_control_group import CheckControlGroupUC


class CheckControlGroupFactory:
    Schema = CheckControlGroupSchema

    @staticmethod
    def create(container: containers.DeclarativeContainer, schema: CheckControlGroupSchema) -> CheckControlGroupUC:
        container.config.update(
            schema.model_dump()
        )

        return container.check_control_group_uc()