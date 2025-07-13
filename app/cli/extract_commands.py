import typer

from app.infra.di import Container

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

    controller = container.data_controller()
    use_case = container.preprocess_data_use_case()
    controller.run(use_case)

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

    controller = container.data_controller()
    use_case = container.preprocess_data_use_case()
    controller.run(use_case)

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

    controller = container.data_controller()
    use_case = container.preprocess_data_use_case()
    controller.run(use_case)
