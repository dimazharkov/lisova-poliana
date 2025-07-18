from dependency_injector import containers, providers

from app.controllers.data_controller import DataController
from app.controllers.experiment_controller import ExperimentController
from app.controllers.extract_controller import ExtractController
from app.core.use_cases.clear_data import ClearDataUseCase
from app.core.use_cases.compute_deltas import ComputeDeltasUseCase
from app.core.use_cases.enrich_data import EnrichDataUseCase
from app.core.use_cases.enrich_delta import EnrichDeltaUseCase
from app.core.use_cases.experiments.baseline_control_experiment import BaselineControlExperimentUseCase
from app.core.use_cases.extract_data import ExtractDataUseCase
from app.core.use_cases.extract_param_duplicates import ExtractParamDuplicatesUseCase
from app.core.use_cases.extract_params import ExtractParamsUseCase
from app.core.use_cases.extract_personal_data import ExtractPersonalDataUseCase
from app.core.use_cases.feature_inspect import FeatureInspectUseCase
from app.core.use_cases.normalize_data import NormalizeDataUseCase
from app.core.use_cases.preprocess_data import PreprocessDataUseCase
from app.infra.evaluators.stat_evaluator import StatEvaluator
from app.repositories.data_repository import DataRepository
from app.repositories.experiment_repository import ExperimentRepository
from app.repositories.json_repository import JsonRepository


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

    data_controller = providers.Factory(
        DataController,
        repo=data_repository
    )

    extract_controller = providers.Factory(
        ExtractController,
        repo=json_repository
    )

    clear_data_use_case = providers.Singleton(
        ClearDataUseCase
    )

    meta_repository = providers.Factory(
        DataRepository,
        source_path=config.META_SOURCE_PATH,
    )

    enrich_data_use_case = providers.Factory(
        EnrichDataUseCase,
        metadata_repository=meta_repository,
        treatment=config.TREATMENT
    )

    normalize_data_use_case = providers.Singleton(
        NormalizeDataUseCase
    )

    compute_deltas_use_case = providers.Singleton(
        ComputeDeltasUseCase
    )

    preprocess_data_use_case = providers.Singleton(
        PreprocessDataUseCase,
        clear_data_use_case=clear_data_use_case,
        enrich_data_use_case=enrich_data_use_case,
        normalize_data_use_case=normalize_data_use_case
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

    enrich_delta_use_case = providers.Factory(
        EnrichDeltaUseCase,
        metadata_repository=meta_repository
    )

    noizy_feature_repository = providers.Factory(
        JsonRepository,
        target_path=config.NOIZY_FEATURE_PATH,
    )

    feature_inspect_use_case = providers.Factory(
        FeatureInspectUseCase,
        repository=noizy_feature_repository,
        include_patterns=config.INCLUDE_PATTERS,
        exclude_fields=config.EXCLUDE_FIELDS
    )

    experiment_repository = providers.Factory(
        ExperimentRepository,
        source_paths=config.SOURCE_PATHS,
        target_folder=config.TARGET_PATH,
        filters=config.FILTERS
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
