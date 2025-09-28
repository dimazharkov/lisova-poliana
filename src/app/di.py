from dependency_injector import providers
from dependency_injector.providers import merge_dicts

from src.app.factories.clear_extracted_data import ClearExtractedDataFactory
from src.app.factories.extract_data_from_raw import ExtractDataFromRawFactory
from src.app.factories.setup_repeat_and_treatment import SetupRepeatAndTreatmentFactory
from src.app.use_cases.clear_extracted_data import ClearExtractedDataUC
from src.app.use_cases.extract_data_from_raw import ExtractDataFromRawUC
from src.app.use_cases.setup_repeat_and_treatment import SetupRepeatAndTreatmentUC
from src.infra.di import Container
from src.infra.repositories.json_file_repository import JsonFileRepository

uc_registry = {
    "extract_data_from_raw": ExtractDataFromRawFactory,
    "clear_extracted_data": ClearExtractedDataFactory,
    "setup_repeat_and_treatment": SetupRepeatAndTreatmentFactory,
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

    clear_extracted_data_uc = providers.Factory(
        ClearExtractedDataUC,
    )

    setup_repeat_and_treatment_uc = providers.Factory(
        SetupRepeatAndTreatmentUC,
        treatment=config.treatment
    )
