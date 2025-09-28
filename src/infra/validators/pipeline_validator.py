from typing import Any

from pydantic import ValidationError

from src.infra.exceptions.pipeline_validation import PipelineValidationException
from src.infra.schemas.pipeline_step import PipelineStepSchema


class PipelineValidator:
    def validate(self, schema: list[dict[str, Any]], uc_repo: dict[str, Any]) -> list[tuple]:
        errors, validated = [], []
        for i, step_schema in enumerate(schema, 1):
            try:
                step = PipelineStepSchema(**step_schema)
            except ValidationError:
                errors.append(f"[{i}] pipeline step schema is invalid")
                continue

            factory = uc_repo.get(step.use_case)
            if factory is None:
                errors.append(f"[{i}] use case {step.use_case} not found")
                continue

            uc_schema = factory.Schema
            if uc_schema:
                try:
                    valid_schema = uc_schema(**step.step_schema)
                except ValidationError:
                    errors.append(f"[{i}] use case {step.use_case} schema is invalid")
                    continue
            else:
                valid_schema = None

            validated.append((step, factory, valid_schema))

        if errors:
            raise PipelineValidationException(errors)

        return validated

