from dependency_injector import containers, providers

from app.controllers.data_controller import DataController
from app.core.use_cases.clear_data import ClearDataUseCase
from app.core.use_cases.enrich_data import EnrichDataUseCase
from app.core.use_cases.normalize_data import NormalizeDataUseCase
from app.core.use_cases.preprocess_data import PreprocessDataUseCase
from app.repositories.data_repository import DataRepository


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    data_repository = providers.Factory(
        DataRepository,
        source_path=config.SOURCE_PATH,
        target_path=config.TARGET_PATH
    )

    data_controller = providers.Factory(
        DataController,
        repo=data_repository
    )

    clear_data_use_case = providers.Singleton(
        ClearDataUseCase
    )

    enrich_data_use_case = providers.Singleton(
        EnrichDataUseCase,
        treatment=config.TREATMENT
    )

    normalize_data_use_case = providers.Singleton(
        NormalizeDataUseCase
    )

    preprocess_data_use_case = providers.Singleton(
        PreprocessDataUseCase,
        clear_data_use_case=clear_data_use_case,
        enrich_data_use_case=enrich_data_use_case,
        normalize_data_use_case=normalize_data_use_case
    )