from dependency_injector import providers
from dependency_injector.providers import merge_dicts

from src.app.factories.extract_data_from_raw import ExtractDataFromRawFactory
from src.app.use_cases.extract_data_from_raw import ExtractDataFromRawUC
from src.infra.di import Container
from src.infra.repositories.json_file_repository import JsonFileRepository

uc_registry = {
    "extract_data_from_raw": ExtractDataFromRawFactory,
    # "write_data_to_disc": WriteDataToDiscFactory,
}

class AppContainer(Container):
    config = Container.config

    uc_registry = providers.Callable(
        merge_dicts,
        Container.uc_registry,
        providers.Object(uc_registry)
    )

    param_repo = providers.Factory(
        JsonFileRepository,
        source_path=config.param_path
    )

    extract_data_from_raw_uc = providers.Factory(
        ExtractDataFromRawUC,
        param_repo=param_repo,
        data_section=config.data_section
    )