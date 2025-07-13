import typer

from app.infra.di import Container

app = typer.Typer()

@app.command()
def from_google():
    pass

@app.command()
def extract(
    source_path: str = typer.Option(
        "", help=""
    ),
    target_path: str = typer.Option(
        "", help=""
    ),
):
    pass

@app.command()
def prep(
        source_path: str = typer.Option(
            "", help=""
        ),
        target_path: str = typer.Option(
            "", help=""
        ),
        treatment: int = typer.Option(
            0, help=""
        )

):
    container = Container()
    container.config.SOURCE_PATH.from_value(source_path)
    container.config.TARGET_PATH.from_value(target_path)
    container.config.TREATMENT.from_value(treatment)

    controller = container.data_controller()
    use_case = container.preprocess_data_use_case()
    controller.run(use_case)
