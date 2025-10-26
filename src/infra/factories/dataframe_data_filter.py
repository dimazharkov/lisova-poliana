from dependency_injector import containers

from src.core.use_cases.dataframe_data_filter import DataFrameDataFilterUC
from src.infra.schemas.dataframe_data_filter import DataFrameDataFilterSchema


class DataFrameDataFilterFactory:
    Schema = DataFrameDataFilterSchema

    @staticmethod
    def create(container: containers.DeclarativeContainer, schema: DataFrameDataFilterSchema) -> DataFrameDataFilterUC:
        container.config.update(
            schema.model_dump()
        )

        return container.dataframe_data_filter_uc()