from dependency_injector import containers

from src.core.use_cases.calc_delta import CalcDeltaUC
from src.infra.schemas.calc_delta import CalcDeltaSchema


class CalcDeltaFactory:
    Schema = CalcDeltaSchema

    @staticmethod
    def create(container: containers.DeclarativeContainer, schema: CalcDeltaSchema) -> CalcDeltaUC:
        container.config.update(
            schema.model_dump()
        )

        return container.calc_delta_uc()