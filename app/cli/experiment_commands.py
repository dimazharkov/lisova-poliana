from typing import List

import typer

from app.infra.di import Container

app = typer.Typer()

@app.command()
def baseline(
        source_path: List[str] = typer.Option(
            ["control_norm.json", "treatment_norm.json"], help=""
        ),
        target_folder: str = typer.Option(
            "baseline", help=""
        )
):
    container = Container()
    container.config.SOURCE_PATHS.from_value(source_path)
    container.config.TARGET_PATH.from_value(target_folder)
    container.config.FILTERS.from_value(
        {
            "repeat": 0 # только начальные данные
        }
    )

    baseline_control_experiment_use_case = container.baseline_control_experiment_use_case()
    experiment_controller = container.experiment_controller()
    experiment_controller.run(baseline_control_experiment_use_case)
