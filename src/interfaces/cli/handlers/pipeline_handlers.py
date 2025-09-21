from src.app.di import AppContainer
from src.app.services.pipeline_service import PipelineService
from src.infra.validators.pipeline_validator import PipelineValidator


def pipeline_run(config_path: str):
    container = AppContainer()

    config_repo = container.config_repo(
        source_path=config_path
    )

    pipeline_validator = PipelineValidator()

    pipeline_service = PipelineService(
        container=container,
        pipeline_validator=pipeline_validator
    )

    pipeline_service.run(
        schema=config_repo.read(),
    )
    print("Pipeline finished!")
