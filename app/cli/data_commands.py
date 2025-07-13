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

    compute_preprocess_data_use_case = container.compute_preprocess_data_use_case()
    data_controller = container.data_controller()
    data_controller.run(compute_preprocess_data_use_case)

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
