from dependency_injector import containers, providers

from app.controllers.data_controller import DataController
from app.controllers.experiment_controller import ExperimentController
from app.controllers.extract_controller import ExtractController
from app.controllers.import_controller import ImportController
from app.controllers.multi_data_controller import MultiDataController
from app.controllers.util_controller import UtilController
from app.core.use_cases.add_personal_data import AddPersonalDataUseCase
from app.core.use_cases.add_personal_indicators import AddPersonalIndicatorsUseCase
from app.core.use_cases.aggregate_data import AggregateDataUseCase
from app.core.use_cases.clear_data import ClearDataUseCase
from app.core.use_cases.build_delta import BuildDeltaUseCase
from app.core.use_cases.add_treatment_data import SetupRepeatAndTreatmentUseCase
from app.core.use_cases.combine_deltas import CombineDeltasUseCase
from app.core.use_cases.experiments.baseline_control import BaselineControlExperimentUseCase
from app.core.use_cases.experiments.before_after import BeforeAfterExperimentUseCase
from app.core.use_cases.experiments.params_before_after import ParamsBeforeAfterExperimentUseCase
from app.core.use_cases.extract_data import ExtractDataUseCase
from app.core.use_cases.extract_param_duplicates import ExtractParamDuplicatesUseCase
from app.core.use_cases.extract_params import ExtractParamsUseCase
from app.core.use_cases.extract_personal_data import ExtractPersonalDataUseCase
from app.core.use_cases.extract_personal_indicators import ExtractPersonalIndicatorsUseCase
from app.core.use_cases.feature_inspect import FeatureInspectUseCase
from app.core.use_cases.normalize_data import NormalizeDataUseCase
from app.core.use_cases.preprocess_data import PreprocessDataUseCase
from app.infra.evaluators.pair_stat_evaluator import PairStatEvaluator
from app.infra.evaluators.stat_evaluator import StatEvaluator
from app.infra.filters.dataframe_column_filter import DataFrameColumnFilter
from app.infra.providers.config_provider import ConfigProvider
from app.infra.filters.column_list_filter import ColumnListFilter
from app.infra.filters.data_filter import DataFilter
from app.repositories.data_repository import DataRepository
from app.repositories.experiment_repository import ExperimentRepository
from app.repositories.indicators_repository import IndicatorsRepository
from app.repositories.json_repository import JsonRepository
from app.repositories.multi_data_repository import MultiDataRepository
from app.repositories.person_repository import PersonRepository


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    data_repository = providers.Factory(
        DataRepository,
        source_path=config.SOURCE_PATH,
        target_path=config.TARGET_PATH
    )

    json_repository = providers.Factory(
        JsonRepository,
        source_path=config.SOURCE_PATH,
        target_path=config.TARGET_PATH
    )

    multi_data_repository = providers.Factory(
        MultiDataRepository,
        source_paths=config.SOURCE_PATHS,
        target_path=config.TARGET_PATH
    )

    data_controller = providers.Factory(
        DataController,
        repo=data_repository
    )

    multi_data_controller = providers.Factory(
        MultiDataController,
        repo=multi_data_repository
    )

    extract_controller = providers.Factory(
        ExtractController,
        repo=json_repository
    )

    clear_data_use_case = providers.Singleton(
        ClearDataUseCase
    )

    combine_deltas_use_case = providers.Singleton(
        CombineDeltasUseCase
    )

    meta_repository = providers.Factory(
        DataRepository,
        source_path=config.META_SOURCE_PATH,
    )

    setup_repeat_and_treatment_use_case = providers.Factory(
        SetupRepeatAndTreatmentUseCase,
        treatment=config.TREATMENT
    )

    column_filter = providers.Factory(
        ColumnListFilter,
        include_patterns=config.INCLUDE_PATTERS,
        exclude_fields=config.EXCLUDE_FIELDS
    )

    normalize_data_use_case = providers.Factory(
        NormalizeDataUseCase,
        column_filter=column_filter
    )

    aggregate_data_use_case = providers.Factory(
        AggregateDataUseCase,
        column_filter=column_filter
    )

    build_delta_use_case = providers.Singleton(
        BuildDeltaUseCase,
        # column_filter=column_filter
    )

    dataframe_column_filter = providers.Factory(
        DataFrameColumnFilter,
        columns=config.COLUMN_NAMES,
        indexes=config.COLUMN_INDEXES,
        keep=config.KEEP_COLUMNS,
    )

    preprocess_data_use_case = providers.Singleton(
        PreprocessDataUseCase,
        clear_data_use_case=clear_data_use_case,
        setup_repeat_and_treatment_use_case=setup_repeat_and_treatment_use_case,
        dataframe_column_filter=dataframe_column_filter
    )

    extract_params_use_case = providers.Singleton(
        ExtractParamsUseCase
    )

    extract_param_duplicates_use_case = providers.Singleton(
        ExtractParamDuplicatesUseCase
    )

    extract_personal_data_use_case = providers.Singleton(
        ExtractPersonalDataUseCase
    )

    extract_personal_indicators_use_case = providers.Singleton(
        ExtractPersonalIndicatorsUseCase
    )

    extract_data_use_case = providers.Factory(
        ExtractDataUseCase,
        data_key=config.DATA_KEY
    )

    noizy_feature_repository = providers.Factory(
        JsonRepository,
        target_path=config.NOIZY_FEATURE_PATH,
    )

    feature_inspect_use_case = providers.Factory(
        FeatureInspectUseCase,
        repository=noizy_feature_repository,
        column_filter=column_filter
    )

    person_repository = providers.Factory(
        PersonRepository,
        source_path=config.META_SOURCE_PATH,
    )

    add_personal_data_use_case = providers.Factory(
        AddPersonalDataUseCase,
        repository=person_repository,
        merge_col=config.MERGE_COL,
        anchor_col=config.ANCHOR_COL
    )

    indicators_repository = providers.Factory(
        IndicatorsRepository,
        source_path=config.META_SOURCE_PATH,
    )

    add_personal_indicators_use_case = providers.Factory(
        AddPersonalIndicatorsUseCase,
        repository=indicators_repository,
        merge_col=config.MERGE_COL,
        anchor_col=config.ANCHOR_COL
    )

    data_filter = providers.Factory(
        DataFilter,
        filters=config.FILTERS
    )

    experiment_repository = providers.Factory(
        ExperimentRepository,
        source_paths=config.SOURCE_PATHS,
        target_folder=config.TARGET_PATH,
        data_filter=data_filter
    )

    experiment_controller = providers.Factory(
        ExperimentController,
        experiment_repository=experiment_repository
    )

    stat_evaluator = providers.Singleton(
        StatEvaluator
    )

    pair_stat_evaluator = providers.Singleton(
        PairStatEvaluator
    )

    chosen_stat_evaluator = providers.Selector(
        config.TEST_TYPE,
        paired=pair_stat_evaluator,
        independent=stat_evaluator,
    )

    config_provider = providers.Factory(
        ConfigProvider,
        source_path=config.CONFIG_PATH
    )

    baseline_control_experiment_use_case = providers.Factory(
        BaselineControlExperimentUseCase,
        stat_evaluator=chosen_stat_evaluator
    )

    before_after_experiment_use_case = providers.Factory(
        BeforeAfterExperimentUseCase,
        stat_evaluator=chosen_stat_evaluator,
        experiment_config=config_provider,
        hue_field=config.HUE_FIELD,
        grouping_fields=config.GROUPING_FIELDS,
        effect_field=config.EFFECT_FIELD
    )

    util_controller = providers.Singleton(
        UtilController,
    )

    import_controller = providers.Singleton(
        ImportController,
    )

    params_before_after_experiment_use_case = providers.Factory(
        ParamsBeforeAfterExperimentUseCase,
        stat_evaluator=chosen_stat_evaluator,
        experiment_config=config_provider,
        experiment_hue=config.HUE_PARAM
    )
