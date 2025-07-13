import typer

from app.infra.di import Container
from app.repositories.json_repository import JsonRepository

app = typer.Typer()

@app.command()
def params(
        source_path: str = typer.Option(
            "", help=""
        ),
        target_path: str = typer.Option(
            "", help=""
        )
):
    container = Container()
    container.config.SOURCE_PATH.from_value(source_path)
    container.config.TARGET_PATH.from_value(target_path)

    extract_params_use_case = container.extract_params_use_case()
    extract_controller = container.extract_controller()
    extract_controller.run(extract_params_use_case)

@app.command()
def param_duplicates(
        source_path: str = typer.Option(
            "", help=""
        ),
        target_path: str = typer.Option(
            "", help=""
        )
):
    container = Container()
    container.config.SOURCE_PATH.from_value(source_path)
    container.config.TARGET_PATH.from_value(target_path)

    extract_param_duplicates_use_case = container.extract_param_duplicates_use_case()
    extract_controller = container.extract_controller()
    extract_controller.run(extract_param_duplicates_use_case)

@app.command()
def data(
        source_path: str = typer.Option(
            "", help=""
        ),
        target_path: str = typer.Option(
            "", help=""
        ),
        params_path: str = typer.Option(
            "", help=""
        ),
        data_key: str = typer.Option(
            "", help=""
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
