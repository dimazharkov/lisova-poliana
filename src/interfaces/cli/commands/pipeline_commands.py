import typer

from src.interfaces.cli.handlers.pipeline_handlers import pipeline_run

app = typer.Typer()

@app.command()
def run(
    config_path: str = typer.Option("", help="Path to the pipeline schema"),
) -> None:
    pipeline_run(config_path=config_path)
