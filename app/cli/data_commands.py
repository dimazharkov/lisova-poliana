from typing import List

import typer

from app.core.use_cases.combine_deltas import CombineDeltasUseCase
from app.infra.di import Container
from app.repositories.data_repository import DataRepository

app = typer.Typer()

@app.command()
def prep(
        source_path: str = typer.Option(
            "", help=""
        ),
        target_path: str = typer.Option(
            "", help=""
        ),
        treatment: int = typer.Option(
            0, help=""
        )

):
    container = Container()
    container.config.SOURCE_PATH.from_value(source_path)
    container.config.TARGET_PATH.from_value(target_path)
    container.config.TREATMENT.from_value(treatment)

    preprocess_data_use_case = container.preprocess_data_use_case()
    data_controller = container.data_controller()
    data_controller.run(preprocess_data_use_case)

@app.command()
def normalize(
        source_path: str = typer.Option(
            "", help=""
        ),
        target_path: str = typer.Option(
            "", help=""
        ),
        include_patterns: List[str] = typer.Option(
            [r"h\d+"], help=""
        ),
        exclude_fields: List[str] = typer.Option(
            [""], help=""
        )
):
    container = Container()
    container.config.SOURCE_PATH.from_value(source_path)
    container.config.TARGET_PATH.from_value(target_path)
    container.config.INCLUDE_PATTERS.from_value(include_patterns)
    container.config.EXCLUDE_FIELDS.from_value(exclude_fields)

    normalize_data_use_case = container.normalize_data_use_case()
    data_controller = container.data_controller()
    data_controller.run(normalize_data_use_case)

@app.command()
def inspect(
        source_path: str = typer.Option(
            "", help=""
        ),
        target_path: str = typer.Option(
            "", help=""
        ),
        noizy_feature_path: str = typer.Option(
            "noizy_features.json", help=""
        ),
        include_patterns: List[str] = typer.Option(
            [r"h\d+"], help=""
        ),
        exclude_fields: List[str] = typer.Option(
            [""], help=""
        )
):
    container = Container()
    container.config.SOURCE_PATH.from_value(source_path)
    container.config.TARGET_PATH.from_value(target_path)
    container.config.NOIZY_FEATURE_PATH.from_value(noizy_feature_path)
    container.config.INCLUDE_PATTERS.from_value(include_patterns)
    container.config.EXCLUDE_FIELDS.from_value(exclude_fields)

    feature_inspect_use_case = container.feature_inspect_use_case()
    data_controller = container.data_controller()
    data_controller.run(feature_inspect_use_case)

@app.command()
def aggregate(
        source_path: str = typer.Option(
            "", help=""
        ),
        target_path: str = typer.Option(
            "", help=""
        ),
        include_patterns: List[str] = typer.Option(
            [r"h\d+"], help=""
        ),
        exclude_fields: List[str] = typer.Option(
            [""], help=""
        )
):
    container = Container()
    container.config.SOURCE_PATH.from_value(source_path)
    container.config.TARGET_PATH.from_value(target_path)
    container.config.INCLUDE_PATTERS.from_value(include_patterns)
    container.config.EXCLUDE_FIELDS.from_value(exclude_fields)

    aggregate_data_use_case = container.aggregate_data_use_case()
    data_controller = container.data_controller()
    data_controller.run(aggregate_data_use_case)

@app.command()
def personalize(
        source_path: str = typer.Option(
            "control_data.json", help=""
        ),
        meta_path: str = typer.Option(
            "personal_data.json", help=""
        ),
        target_path: str = typer.Option(
            "control_data.json", help=""
        ),
        anchor_col: str = typer.Option(
            "h1", help=""
        ),
):
    container = Container()
    container.config.SOURCE_PATH.from_value(source_path)
    container.config.META_SOURCE_PATH.from_value(meta_path)
    container.config.TARGET_PATH.from_value(target_path)
    container.config.ANCHOR_COL.from_value(anchor_col)

    add_personal_data_use_case = container.add_personal_data_use_case()
    data_controller = container.data_controller()
    data_controller.run(add_personal_data_use_case)
