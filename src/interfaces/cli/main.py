import typer

from src.interfaces.cli.commands import pipeline_commands

app = typer.Typer()
app.add_typer(pipeline_commands.app, name="pipeline")

if __name__ == "__main__":
    app()