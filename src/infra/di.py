from dependency_injector import containers, providers

from src.core.use_cases.read_data_from_disc import ReadDataFromDiscUC
from src.core.use_cases.read_json_from_disc import ReadJsonFromDiscUC
from src.core.use_cases.write_data_to_disc import WriteDataToDiscUC
from src.core.use_cases.write_json_to_disc import WriteJsonToDiscUC
from src.infra.factories.read_data_from_disc import ReadDataFromDiscFactory
from src.infra.factories.read_json_from_disc import ReadJsonFromDiscFactory
from src.infra.factories.write_data_to_disc import WriteDataToDiscFactory
from src.infra.factories.write_json_to_disc import WriteJsonToDiscFactory
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

    uc_registry = providers.Object({
        "read_data_from_disc": ReadDataFromDiscFactory,
        "read_json_from_disc": ReadJsonFromDiscFactory,
        "write_data_to_disc": WriteDataToDiscFactory,
        "write_json_to_disc": WriteJsonToDiscFactory,
    })