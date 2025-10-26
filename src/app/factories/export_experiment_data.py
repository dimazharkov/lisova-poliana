from dependency_injector import containers

from src.app.schemas.export_experiment_data import ExportExperimentDataSchema
from src.app.use_cases.export_experiment_data import ExportExperimentDataUC


class ExportExperimentDataFactory:
    Schema = ExportExperimentDataSchema

    @staticmethod
    def create(container: containers.DeclarativeContainer, schema: ExportExperimentDataSchema) -> ExportExperimentDataUC:
        container.config.update(
            schema.model_dump()
        )

        return container.export_experiment_data_uc()