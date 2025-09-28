from dependency_injector import containers

from src.core.use_cases.dataframe_column_filter import DataFrameColumnFilterUC
from src.infra.schemas.dataframe_column_filter import DataFrameColumnFilterSchema


class DataFrameColumnFilterFactory:
    Schema = DataFrameColumnFilterSchema

    @staticmethod
    def create(container: containers.DeclarativeContainer, schema: DataFrameColumnFilterSchema) -> DataFrameColumnFilterUC:
        container.config.update(
            schema.model_dump()
        )

        return container.dataframe_column_filter_uc()