from typing import List

import typer

from app.core.use_cases.combine_deltas import CombineDeltasUseCase
from app.infra.di import Container
from app.repositories.data_repository import DataRepository

app = typer.Typer()

@app.command()
def from_google():
    pass

@app.command()
def prep(
        source_path: str = typer.Option(
            "", help=""
        ),
        meta_path: str = typer.Option(
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
    container.config.META_SOURCE_PATH.from_value(meta_path)
    container.config.TARGET_PATH.from_value(target_path)
    container.config.TREATMENT.from_value(treatment)

    preprocess_data_use_case = container.preprocess_data_use_case()
    data_controller = container.data_controller()
    data_controller.run(preprocess_data_use_case)

@app.command()
def compute_deltas(
        source_path: str = typer.Option(
            "", help=""
        ),
        target_path: str = typer.Option(
            "", help=""
        )
):
    container = Container()
    container.config.SOURCE_PATH.from_value(source_path)
    container.config.TARGET_PATH.from_value(target_path)

    compute_deltas_use_case = container.compute_deltas_use_case()
    data_controller = container.data_controller()
    data_controller.run(compute_deltas_use_case)

@app.command()
def combine_deltas(
        delta1_path: str = typer.Option(
            "", help=""
        ),
        delta2_path: str = typer.Option(
            "", help=""
        ),
        target_path: str = typer.Option(
            "", help=""
        )
):
    delta1_repo = DataRepository(source_path=delta1_path)
    delta2_repo = DataRepository(source_path=delta2_path)

    combine_deltas_use_case = CombineDeltasUseCase()
    data = combine_deltas_use_case.run([delta1_repo.all(), delta2_repo.all()])

    combined_repo = DataRepository(target_path=target_path)
    combined_repo.save(data)

@app.command()
def enrich_delta(
        source_path: str = typer.Option(
            "combined_delta.json", help=""
        ),
        meta_path: str = typer.Option(
            "personal_data.json", help=""
        ),
        target_path: str = typer.Option(
            "delta.json", help=""
        )
):
    container = Container()
    container.config.SOURCE_PATH.from_value(source_path)
    container.config.META_SOURCE_PATH.from_value(meta_path)
    container.config.TARGET_PATH.from_value(target_path)

    enrich_delta_use_case = container.enrich_delta_use_case()
    data_controller = container.data_controller()
    data_controller.run(enrich_delta_use_case)

@app.command()
def delta_feature_inspect(
        source_path: str = typer.Option(
            "delta.json", help=""
        ),
        noizy_feature_path: str = typer.Option(
            "noizy_features.json", help=""
        ),
        target_path: str = typer.Option(
            "clean_delta.json", help=""
        ),
        include_patterns: List[str] = typer.Option(
            ["*_norm"], help=""
        ),
        exclude_fields: List[str] = typer.Option(
            [""], help=""
        )
):
    container = Container()
    container.config.SOURCE_PATH.from_value(source_path)
    container.config.NOIZY_FEATURE_PATH.from_value(noizy_feature_path)
    container.config.TARGET_PATH.from_value(target_path)
    container.config.INCLUDE_PATTERS.from_value(include_patterns)
    container.config.EXCLUDE_FIELDS.from_value(exclude_fields)

    feature_inspect_use_case = container.feature_inspect_use_case()
    data_controller = container.data_controller()
    data_controller.run(feature_inspect_use_case)
