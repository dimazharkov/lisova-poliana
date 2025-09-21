from typing import Any, Optional

from src.app.di import AppContainer
from src.core.contracts.use_case import DataUseCase, NoInputUseCase
from src.infra.schemas.pipeline_step import PipelineStepSchema
from src.infra.validators.pipeline_validator import PipelineValidator


def is_expects_input(use_case: Any) -> bool:
    if isinstance(use_case, DataUseCase):   # type: ignore[arg-type]
        return True
    if isinstance(use_case, NoInputUseCase):  # type: ignore[arg-type]
        return False
    raise TypeError(f"Unknown use case type: {type(use_case).__name__}")


class PipelineService:
    def __init__(self, container: AppContainer, pipeline_validator: PipelineValidator):
        self.container = container
        self.pipeline_validator = pipeline_validator

    def run(self, schema: list[dict], initial_data: Optional[Any] = None) -> None:
        uc_registry = self.container.uc_registry()

        pipeline_steps = self.pipeline_validator.validate(
            schema, uc_registry
        )

        pipeline: list[tuple[PipelineStepSchema, Any, bool]] = []
        for step, factory, step_schema in pipeline_steps:
            use_case = factory.create(
                self.container,
                step_schema
            )
            expects_input = is_expects_input(use_case)
            pipeline.append((step, use_case, expects_input))

        data: Any = initial_data
        for step, use_case, expects_input in pipeline:
            data = use_case.run(data) if expects_input else use_case.run()
            res_text = f"{step.name} [{step.use_case}]"
            print(f"{res_text:.<60} ok")
        return data

