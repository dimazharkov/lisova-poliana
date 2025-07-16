import typer

from app.infra.di import Container
from app.repositories.json_repository import JsonRepository

app = typer.Typer()

@app.command()
def params(
        source_path: str = typer.Option(
            "raw_data.json", help=""
        ),
        target_path: str = typer.Option(
            "params.json", help=""
        )
):
    container = Container()
    container.config.SOURCE_PATH.from_value(source_path)
    container.config.TARGET_PATH.from_value(target_path)

    extract_params_use_case = container.extract_params_use_case()
    extract_controller = container.extract_controller()
    extract_controller.extract(extract_params_use_case)

@app.command()
def param_duplicates(
        source_path: str = typer.Option(
            "params.json", help=""
        ),
        target_path: str = typer.Option(
            "param-duplicates.json", help=""
        )
):
    container = Container()
    container.config.SOURCE_PATH.from_value(source_path)
    container.config.TARGET_PATH.from_value(target_path)

    extract_param_duplicates_use_case = container.extract_param_duplicates_use_case()
    extract_controller = container.extract_controller()
    extract_controller.extract(extract_param_duplicates_use_case)

@app.command()
def data(
        source_path: str = typer.Option(
            "raw_data.json", help=""
        ),
        target_path: str = typer.Option(
            "", help="Результат в: control_data.json или treatment_data.json"
        ),
        params_path: str = typer.Option(
            "params.json", help=""
        ),
        data_key: str = typer.Option(
            "", help="Вкладки: 'контроль' или 'Дих'"
        )
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

@app.command()
def personal_data(
        source_path: str = typer.Option(
            "raw_data.json", help=""
        ),
        target_path: str = typer.Option(
            "personal_data.json", help=""
        )
):
    container = Container()
    container.config.SOURCE_PATH.from_value(source_path)
    container.config.TARGET_PATH.from_value(target_path)

    extract_personal_data_use_case = container.extract_personal_data_use_case()
    extract_controller = container.extract_controller()
    extract_controller.extract(extract_personal_data_use_case)
