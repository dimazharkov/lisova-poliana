from typing import List

import typer

from app.cli.handlers.delta_handlers import delta_build, delta_combine
from app.infra.di import Container

app = typer.Typer()

@app.command()
def build(
        source_path: str = typer.Option(
            "", help=""
        ),
        target_path: str = typer.Option(
            "", help=""
        ),
):
    delta_build(
        source_path=source_path,
        target_path=target_path
    )

@app.command()
def combine(
        source_path: List[str] = typer.Option(
            ["control_delta.json", "treatment_delta.json"], help=""
        ),
        target_path: str = typer.Option(
            "delta.json", help=""
        ),
):
    delta_combine(
        source_path=source_path,
        target_path=target_path
    )
