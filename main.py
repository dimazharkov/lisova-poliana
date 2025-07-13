import typer

from app.cli import experiment_commands, data_commands

app = typer.Typer()
app.add_typer(experiment_commands.app, name="experiment")
app.add_typer(data_commands.app, name="data")

if __name__ == "__main__":
    app()
