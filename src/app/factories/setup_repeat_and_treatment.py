from dependency_injector import containers

from src.app.schemas.setup_repeat_and_treatment import SetupRepeatAndTreatmentSchema
from src.app.use_cases.setup_repeat_and_treatment import SetupRepeatAndTreatmentUC


class SetupRepeatAndTreatmentFactory:
    Schema = SetupRepeatAndTreatmentSchema

    @staticmethod
    def create(container: containers.DeclarativeContainer, schema: SetupRepeatAndTreatmentSchema) -> SetupRepeatAndTreatmentUC:
        container.config.update(
            schema.model_dump()
        )

        return container.setup_repeat_and_treatment_uc()