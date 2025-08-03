import typer

from app.cli.handlers.util_handlers import util_experiment_map_file, util_export_experiment_data
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
    util_experiment_map_file(
        source_path=source_path,
        config_path=config_path
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
    util_export_experiment_data(
        source_path=source_path,
        config_path=config_path
    )
