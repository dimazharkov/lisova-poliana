from dependency_injector import containers, providers

from app.core.use_cases.add_personal_data import AddPersonalDataUseCase
from src.core.use_cases.add_columns import AddColumnsUC
from src.core.use_cases.aggregate_data import AggregateDataUC
from src.core.use_cases.calc_delta import CalcDeltaUC
from src.core.use_cases.combine_datasets import CombineDatasetsUC
from src.core.use_cases.dataframe_column_filter import DataFrameColumnFilterUC
from src.core.use_cases.dataframe_data_filter import DataFrameDataFilterUC
from src.core.use_cases.normalize_data import NormalizeDataUC
from src.core.use_cases.read_data_from_disc import ReadDataFromDiscUC
from src.core.use_cases.read_json_from_disc import ReadJsonFromDiscUC
from src.core.use_cases.two_sample_analysis import TwoSampleAnalysisUC
from src.core.use_cases.write_data_to_disc import WriteDataToDiscUC
from src.core.use_cases.write_json_to_disc import WriteJsonToDiscUC
from src.infra.calculators.stat.independent_stat_calculator import IndependentStatCalculator
from src.infra.calculators.stat.pairwise_stat_calculator import PairwiseStatCalculator
from src.infra.factories.add_columns import AddColumnsFactory
from src.infra.factories.aggregate_data import AggregateDataFactory
from src.infra.factories.calc_delta import CalcDeltaFactory
from src.infra.factories.combine_datasets import CombineDatasetsFactory
from src.infra.factories.dataframe_column_filter import DataFrameColumnFilterFactory
from src.infra.factories.dataframe_data_filter import DataFrameDataFilterFactory
from src.infra.factories.normalize_data import NormalizeDataFactory
from src.infra.factories.read_data_from_disc import ReadDataFromDiscFactory
from src.infra.factories.read_json_from_disc import ReadJsonFromDiscFactory
from src.infra.factories.two_sample_analysis import TwoSampleAnalysisFactory
from src.infra.factories.write_data_to_disc import WriteDataToDiscFactory
from src.infra.factories.write_json_to_disc import WriteJsonToDiscFactory
from src.infra.filters.column_list_filter import ColumnListFilter
from src.infra.filters.data_frame_filter import DataFrameFilter
from src.infra.repositories.data_file_repository import DataFileRepository
from src.infra.repositories.experiment_repository import ExperimentRepository
from src.infra.repositories.json_file_repository import JsonFileRepository
from src.infra.schemas.add_columns import AddColumnsSchema
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
        keep=config.keep
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

    independent_stat_calculator = providers.Singleton(
        IndependentStatCalculator
    )

    pairwise_stat_calculator = providers.Singleton(
        PairwiseStatCalculator
    )

    chosen_stat_calculator = providers.Selector(
        config.test_type,
        paired=pairwise_stat_calculator,
        independent=independent_stat_calculator,
    )

    df_filter = providers.Factory(
        DataFrameFilter,
        filter_config=config.filter_config
    )

    experiment_repository = providers.Factory(
        ExperimentRepository,
        target_folder=config.target_folder
    )

    two_sample_analysis_uc = providers.Factory(
        TwoSampleAnalysisUC,
        stat_calculator=chosen_stat_calculator,
        df_filter=df_filter,
        repository=experiment_repository,
        hue_field=config.hue_field,
        effect_field=config.effect_field,
        stratify_fields=config.stratify_fields,
        index_fields=config.index_fields,
        experiment_config=config.experiment_config,
        test_method=config.test_method
    )

    calc_delta_uc = providers.Factory(
        CalcDeltaUC,
        method=config.method,
        group_cols=config.group_cols,
        sort_col=config.sort_col,
        service_cols=config.service_cols
    )

    combine_datasets_uc = providers.Factory(
        CombineDatasetsUC,
        how=config.how,
        enforce_same_dtypes=config.enforce_same_dtypes,
        add_source_col=config.add_source_col,
        fill_value=config.fill_value
    )

    add_columns_uc = providers.Factory(
        AddColumnsUC,
        loc=config.loc,
        columns=config.columns
    )

    dataframe_data_filter_uc = providers.Factory(
        DataFrameDataFilterUC,
        df_filter=df_filter
    )

    uc_registry = providers.Object({
        "read_data_from_disc": ReadDataFromDiscFactory,
        "read_json_from_disc": ReadJsonFromDiscFactory,
        "write_data_to_disc": WriteDataToDiscFactory,
        "write_json_to_disc": WriteJsonToDiscFactory,
        "dataframe_column_filter":  DataFrameColumnFilterFactory,
        "dataframe_data_filter": DataFrameDataFilterFactory,
        "normalize_data": NormalizeDataFactory,
        "aggregate_data": AggregateDataFactory,
        "two_sample_analysis": TwoSampleAnalysisFactory,
        "calc_delta": CalcDeltaFactory,
        "combine_datasets": CombineDatasetsFactory,
        "add_columns": AddColumnsFactory
    })