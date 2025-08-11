import typer

from app.cli.handlers.pipeline_handlers import pipeline_overall, pipeline_first, pipeline_second, pipeline_third, \
    pipeline_fourth

app = typer.Typer()

@app.command()
def overall():
    pipeline_overall()

@app.command()
def first():
    pipeline_first()

@app.command()
def second():
    pipeline_second()

@app.command()
def third():
    pipeline_third()

@app.command()
def fourth():
    pipeline_fourth()
