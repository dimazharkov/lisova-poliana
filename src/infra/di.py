from dependency_injector import containers, providers

from src.core.use_cases.aggregate_data import AggregateDataUC
from src.core.use_cases.dataframe_column_filter import DataFrameColumnFilterUC
from src.core.use_cases.normalize_data import NormalizeDataUC
from src.core.use_cases.read_data_from_disc import ReadDataFromDiscUC
from src.core.use_cases.read_json_from_disc import ReadJsonFromDiscUC
from src.core.use_cases.write_data_to_disc import WriteDataToDiscUC
from src.core.use_cases.write_json_to_disc import WriteJsonToDiscUC
from src.infra.factories.aggregate_data import AggregateDataFactory
from src.infra.factories.dataframe_column_filter import DataFrameColumnFilterFactory
from src.infra.factories.normalize_data import NormalizeDataFactory
from src.infra.factories.read_data_from_disc import ReadDataFromDiscFactory
from src.infra.factories.read_json_from_disc import ReadJsonFromDiscFactory
from src.infra.factories.write_data_to_disc import WriteDataToDiscFactory
from src.infra.factories.write_json_to_disc import WriteJsonToDiscFactory
from src.infra.filters.column_list_filter import ColumnListFilter
from src.infra.repositories.data_file_repository import DataFileRepository
from src.infra.repositories.json_file_repository import JsonFileRepository
from src.infra.validators.pipeline_validator import PipelineValidator


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    pipeline_validator = providers.Singleton(
        PipelineValidator
    )

    data_repo = providers.Factory(
        DataFileRepository,
        source_path=config.source_path,
        target_path=config.target_path
    )

    config_repo = providers.Factory(
        JsonFileRepository,
        source_path=config.source_path
    )

    json_repo = providers.Factory(
        JsonFileRepository,
        source_path=config.source_path,
        target_path=config.target_path
    )

    read_data_from_disc_uc = providers.Factory(
        ReadDataFromDiscUC,
        data_repo=data_repo
    )

    read_json_from_disc_uc = providers.Factory(
        ReadJsonFromDiscUC,
        data_repo=json_repo
    )

    write_data_to_disc_uc = providers.Factory(
        WriteDataToDiscUC,
        data_repo=data_repo
    )

    write_json_to_disc_uc = providers.Factory(
        WriteJsonToDiscUC,
        data_repo=json_repo
    )

    dataframe_column_filter_uc = providers.Factory(
        DataFrameColumnFilterUC,
        columns=config.columns,
        indexes=config.indexes,
        keep=config.keep_columns
    )

    column_list_filter = providers.Factory(
        ColumnListFilter,
        include_patterns=config.include_patterns,
        exclude_fields=config.exclude_fields
    )

    normalize_data_uc = providers.Factory(
        NormalizeDataUC,
        column_filter=column_list_filter,
        scallers=config.scalers
    )

    aggregate_data_uc = providers.Factory(
        AggregateDataUC,
        column_filter=column_list_filter,
        agg_method=config.agg_method,
        agg_field=config.agg_field
    )

    uc_registry = providers.Object({
        "read_data_from_disc": ReadDataFromDiscFactory,
        "read_json_from_disc": ReadJsonFromDiscFactory,
        "write_data_to_disc": WriteDataToDiscFactory,
        "write_json_to_disc": WriteJsonToDiscFactory,
        "dataframe_column_filter":  DataFrameColumnFilterFactory,
        "normalize_data": NormalizeDataFactory,
        "aggregate_data": AggregateDataFactory,
    })