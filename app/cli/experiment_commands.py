from typing import List, Literal

import typer

from app.cli.handlers.experiment_handlers import experiment_baseline, experiment_before_after, \
    experiment_control_treatment, experiment_params_before_after, experiment_params_delta_before_after
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
    experiment_baseline(
        source_path=source_path,
        target_folder=target_folder
    )

@app.command()
def before_after(
        source_path: List[str] = typer.Option(
            ["control_norm.json"], help=""
        ),
        target_folder: str = typer.Option(
            "before-after/control-3", help=""
        ),
        experiment: str = typer.Option(
            "3", help=""
        ),
        config_path: str = typer.Option(
            "config.json", help=""
        ),
        test_type: str = typer.Option(
            "independent", help=""
        ),
        hue_field: str = typer.Option(
            "repeat", help=""
        ),
        effect_field: str = typer.Option(
            "median_effect", help=""
        ),
        index_field: List[str] = typer.Option(
            ["person"], help=""
        ),
        grouping_field: List[str] = typer.Option(
            [], help=""
        ),

):
    experiment_before_after(
        source_path=source_path,
        target_folder=target_folder,
        experiment=experiment,
        config_path=config_path,
        test_type=test_type,
        hue_field=hue_field,
        effect_field=effect_field,
        index_fields=index_field,
        grouping_fields=grouping_field
    )

@app.command()
def control_treatment(
        source_path: List[str] = typer.Option(
            ["control_norm.json"], help=""
        ),
        target_folder: str = typer.Option(
            "before-after/control-3", help=""
        ),
        experiment: str = typer.Option(
            "3", help=""
        ),
        config_path: str = typer.Option(
            "config.json", help=""
        )
):
    experiment_control_treatment(
        source_path=source_path,
        target_folder=target_folder,
        experiment=experiment,
        config_path=config_path
    )

@app.command()
def params_before_after(
        source_path: List[str] = typer.Option(
            ["control_norm.json"], help=""
        ),
        target_folder: str = typer.Option(
            "before-after/control-3", help=""
        ),
        experiment: str = typer.Option(
            "3", help=""
        ),
        config_path: str = typer.Option(
            "config.json", help=""
        ),
        test_type: str = typer.Option(
            "independent", help="pair or independent"
        )
):
    experiment_params_before_after(
        source_path=source_path,
        target_folder=target_folder,
        experiment=experiment,
        config_path=config_path,
        test_type=test_type
    )

@app.command()
def params_delta_before_after(
        source_path: List[str] = typer.Option(
            ["control_norm.json"], help=""
        ),
        target_folder: str = typer.Option(
            "before-after/control-3", help=""
        ),
        experiment: str = typer.Option(
            "3", help=""
        ),
        config_path: str = typer.Option(
            "config.json", help=""
        )
):
    experiment_params_delta_before_after(
        source_path=source_path,
        target_folder=target_folder,
        experiment=experiment,
        config_path=config_path
    )

