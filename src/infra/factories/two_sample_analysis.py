from dependency_injector import containers

from src.core.use_cases.two_sample_analysis import TwoSampleAnalysisUC
from src.infra.schemas.two_sample_analysis import TwoSampleAnalysisSchema


class TwoSampleAnalysisFactory:
    Schema = TwoSampleAnalysisSchema

    @staticmethod
    def create(container: containers.DeclarativeContainer, schema: TwoSampleAnalysisSchema) -> TwoSampleAnalysisUC:
        container.config.update(
            schema.model_dump()
        )

        return container.two_sample_analysis_uc()