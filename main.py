import typer

from app.cli import experiment_commands, data_commands, extract_commands, test_commands, delta_commands

app = typer.Typer()
app.add_typer(experiment_commands.app, name="experiment")
app.add_typer(extract_commands.app, name="extract")
app.add_typer(data_commands.app, name="data")
app.add_typer(delta_commands.app, name="delta")
app.add_typer(test_commands.app, name="test")

if __name__ == "__main__":
    app()
