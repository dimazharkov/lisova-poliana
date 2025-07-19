from typing import List

import typer

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
    container = Container()
    container.config.SOURCE_PATH.from_value(source_path)
    container.config.TARGET_PATH.from_value(target_path)

    build_delta_use_case = container.build_delta_use_case()
    data_controller = container.data_controller()
    data_controller.run(build_delta_use_case)

@app.command()
def combine(
        source_path: List[str] = typer.Option(
            ["control_delta.json", "treatment_delta.json"], help=""
        ),
        target_path: str = typer.Option(
            "delta.json", help=""
        ),
):
    container = Container()
    container.config.SOURCE_PATHS.from_value(source_path)
    container.config.TARGET_PATH.from_value(target_path)

    combine_deltas_use_case = container.combine_deltas_use_case()
    multi_data_controller = container.multi_data_controller()
    multi_data_controller.run(combine_deltas_use_case)
