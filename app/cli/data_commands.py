from typing import List

import typer

from app.cli.handlers.data_handlers import (
    data_preparation, data_normalize, data_inspect,
    data_aggregate, data_personalize, data_add_indicators
)

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
    data_preparation(
        source_path=source_path,
        target_path=target_path,
        treatment=treatment
    )

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
    data_normalize(
        source_path=source_path,
        target_path=target_path,
        include_patterns=include_patterns,
        exclude_fields=exclude_fields
    )

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
    data_inspect(
        source_path=source_path,
        target_path=target_path,
        noizy_feature_path=noizy_feature_path,
        include_patterns=include_patterns,
        exclude_fields=exclude_fields
    )

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
    data_aggregate(
        source_path=source_path,
        target_path=target_path,
        include_patterns=include_patterns,
        exclude_fields=exclude_fields
    )

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
        merge_col: str = typer.Option(
            "person", help="Колонка по которой смержить данные"
        ),
        anchor_col: str = typer.Option(
            "h1", help="Колонка перед которой вставить данные"
        ),
):
    data_personalize(
        source_path=source_path,
        meta_path=meta_path,
        target_path=target_path,
        merge_col=merge_col,
        anchor_col=anchor_col
    )

@app.command()
def add_indicators(
        source_path: str = typer.Option(
            "control_data.json", help=""
        ),
        meta_path: str = typer.Option(
            "personal_indicators_data.json", help=""
        ),
        target_path: str = typer.Option(
            "control_data.json", help=""
        ),
        merge_col: str = typer.Option(
            "person", help="Колонка по которой смержить данные"
        ),
        anchor_col: str = typer.Option(
            "h1", help="Колонка перед которой вставить данные"
        ),
):
    data_add_indicators(
        source_path=source_path,
        meta_path=meta_path,
        target_path=target_path,
        merge_col=merge_col,
        anchor_col=anchor_col
    )

