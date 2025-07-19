from dependency_injector import containers, providers

from app.controllers.data_controller import DataController
from app.controllers.experiment_controller import ExperimentController
from app.controllers.extract_controller import ExtractController
from app.controllers.multi_data_controller import MultiDataController
from app.core.use_cases.add_personal_data import AddPersonalDataUseCase
from app.core.use_cases.aggregate_data import AggregateDataUseCase
from app.core.use_cases.clear_data import ClearDataUseCase
from app.core.use_cases.build_delta import BuildDeltaUseCase
from app.core.use_cases.add_treatment_data import SetupRepeatAndTreatmentUseCase
from app.core.use_cases.combine_deltas import CombineDeltasUseCase
from app.core.use_cases.experiments.baseline_control import BaselineControlExperimentUseCase
from app.core.use_cases.extract_data import ExtractDataUseCase
from app.core.use_cases.extract_param_duplicates import ExtractParamDuplicatesUseCase
from app.core.use_cases.extract_params import ExtractParamsUseCase
from app.core.use_cases.extract_personal_data import ExtractPersonalDataUseCase
from app.core.use_cases.feature_inspect import FeatureInspectUseCase
from app.core.use_cases.normalize_data import NormalizeDataUseCase
from app.core.use_cases.preprocess_data import PreprocessDataUseCase
from app.infra.evaluators.stat_evaluator import StatEvaluator
from app.infra.filters.column_filter import ColumnFilter
from app.infra.filters.data_filter import DataFilter
from app.repositories.data_repository import DataRepository
from app.repositories.experiment_repository import ExperimentRepository
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
        ColumnFilter,
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

    preprocess_data_use_case = providers.Singleton(
        PreprocessDataUseCase,
        clear_data_use_case=clear_data_use_case,
        setup_repeat_and_treatment_use_case=setup_repeat_and_treatment_use_case
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

    baseline_control_experiment_use_case = providers.Factory(
        BaselineControlExperimentUseCase,
        stat_evaluator=stat_evaluator
    )

    person_repository = providers.Factory(
        PersonRepository,
        source_path=config.META_SOURCE_PATH,
    )

    add_personal_data_use_case = providers.Factory(
        AddPersonalDataUseCase,
        repository=person_repository,
        anchor_col=config.ANCHOR_COL
    )
