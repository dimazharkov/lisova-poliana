from dependency_injector import providers
from dependency_injector.providers import merge_dicts

from src.app.factories.add_personal_data import AddPersonalDataFactory
from src.app.factories.add_personal_indicators import AddPersonalIndicatorsFactory
from src.app.factories.clear_extracted_data import ClearExtractedDataFactory
from src.app.factories.export_experiment_data import ExportExperimentDataFactory
from src.app.factories.extract_data_from_raw import ExtractDataFromRawFactory
from src.app.factories.setup_repeat_and_treatment import SetupRepeatAndTreatmentFactory
from src.app.resources.indicators_data import IndicatorsData
from src.app.resources.person_data import PersonData
from src.app.use_cases.add_personal_data import AddPersonalDataUC
from src.app.use_cases.add_personal_indicators import AddPersonalIndicatorsUC
from src.app.use_cases.clear_extracted_data import ClearExtractedDataUC
from src.app.use_cases.export_experiment_data import ExportExperimentDataUC
from src.app.use_cases.extract_data_from_raw import ExtractDataFromRawUC
from src.app.use_cases.setup_repeat_and_treatment import SetupRepeatAndTreatmentUC
from src.infra.di import Container
from src.infra.providers.config_provider import ConfigProvider
from src.infra.repositories.json_file_repository import JsonFileRepository

uc_registry = {
    "extract_data_from_raw": ExtractDataFromRawFactory,
    "clear_extracted_data": ClearExtractedDataFactory,
    "setup_repeat_and_treatment": SetupRepeatAndTreatmentFactory,
    "add_personal_data": AddPersonalDataFactory,
    "add_personal_indicators": AddPersonalIndicatorsFactory,
    "export_experiment_data": ExportExperimentDataFactory,
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

    person_repo = providers.Factory(
        PersonData,
        source_path=config.meta_path
    )

    add_personal_data_uc = providers.Factory(
        AddPersonalDataUC,
        personal_repo=person_repo,
        merge_column=config.merge_column,
        anchor_column=config.anchor_column
    )

    indicators_repo = providers.Factory(
        IndicatorsData,
        source_path=config.meta_path
    )

    add_personal_indicators_uc = providers.Factory(
        AddPersonalIndicatorsUC,
        indicators_repo=indicators_repo,
        merge_column=config.merge_column,
        anchor_column=config.anchor_column
    )

    config_provider = providers.Factory(
        ConfigProvider,
        source_path=config.config_path
    )

    export_experiment_data_uc = providers.Factory(
        ExportExperimentDataUC,
        source_path=config.source_path,
        target_path=config.target_path,
        provider=config_provider
    )


