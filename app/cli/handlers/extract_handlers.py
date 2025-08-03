from app.infra.di import Container
from app.repositories.json_repository import JsonRepository


def extract_params(
        source_path: str,
        target_path: str
):
    container = Container()
    container.config.SOURCE_PATH.from_value(source_path)
    container.config.TARGET_PATH.from_value(target_path)

    extract_params_use_case = container.extract_params_use_case()
    extract_controller = container.extract_controller()
    extract_controller.extract(extract_params_use_case)

def extract_param_duplicates(
        source_path: str,
        target_path: str
):
    container = Container()
    container.config.SOURCE_PATH.from_value(source_path)
    container.config.TARGET_PATH.from_value(target_path)

    extract_param_duplicates_use_case = container.extract_param_duplicates_use_case()
    extract_controller = container.extract_controller()
    extract_controller.extract(extract_param_duplicates_use_case)

def extract_data(
        source_path: str,
        target_path: str,
        params_path: str,
        data_key: str
):
    container = Container()
    container.config.SOURCE_PATH.from_value(source_path)
    container.config.TARGET_PATH.from_value(target_path)
    container.config.PARAMS_PATH.from_value(params_path)
    container.config.DATA_KEY.from_value(data_key)


    extract_data_use_case = container.extract_data_use_case()
    param_repo = JsonRepository(
        source_path=params_path, target_path=params_path
    )

    extract_controller = container.extract_controller()
    extract_controller.extract_data(
        extract_data_use_case, param_repo
    )

def extract_personal_data(
        source_path: str,
        target_path: str
):
    container = Container()
    container.config.SOURCE_PATH.from_value(source_path)
    container.config.TARGET_PATH.from_value(target_path)

    extract_personal_data_use_case = container.extract_personal_data_use_case()
    extract_controller = container.extract_controller()
    extract_controller.extract(extract_personal_data_use_case)

def extract_personal_indicators(
        source_path: str,
        target_path: str
):
    container = Container()
    container.config.SOURCE_PATH.from_value(source_path)
    container.config.TARGET_PATH.from_value(target_path)

    extract_personal_indicators_use_case = container.extract_personal_indicators_use_case()
    extract_controller = container.extract_controller()
    extract_controller.extract(extract_personal_indicators_use_case)
