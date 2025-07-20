import typer

from app.infra.di import Container

app = typer.Typer()

@app.command()
def experiment_map_file(
        source_path: str = typer.Option(
            "", help=""
        ),
        config_path: str = typer.Option(
            "config.json", help=""
        )
):
    container = Container()
    container.config.CONFIG_PATH.from_value(config_path)
    util_controller = container.util_controller()
    config_provider = container.config_provider()

    util_controller.experiment_map_file(
        source_path=source_path,
        config_provider=config_provider
    )

@app.command()
def export_experiment_data(
        source_path: str = typer.Option(
            "", help=""
        ),
        config_path: str = typer.Option(
            "config.json", help=""
        )
):
    container = Container()
    container.config.CONFIG_PATH.from_value(config_path)
    util_controller = container.util_controller()
    config_provider = container.config_provider()

    util_controller.export_experiment_data(
        source_path=source_path,
        config_provider=config_provider
    )

