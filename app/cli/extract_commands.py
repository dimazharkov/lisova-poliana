import typer

from app.cli.handlers.extract_handlers import extract_params, extract_param_duplicates, extract_data, \
    extract_personal_data, extract_personal_indicators
from app.infra.di import Container
from app.repositories.json_repository import JsonRepository

app = typer.Typer()

@app.command()
def params(
        source_path: str = typer.Option(
            "raw_data.json", help=""
        ),
        target_path: str = typer.Option(
            "params.json", help=""
        )
):
    extract_params(
        source_path=source_path,
        target_path=target_path
    )

@app.command()
def param_duplicates(
        source_path: str = typer.Option(
            "params.json", help=""
        ),
        target_path: str = typer.Option(
            "param-duplicates.json", help=""
        )
):
    extract_param_duplicates(
        source_path=source_path,
        target_path=target_path
    )

@app.command()
def data(
        source_path: str = typer.Option(
            "source/raw_data.json", help=""
        ),
        target_path: str = typer.Option(
            "", help="Результат в: control_data.json или treatment_data.json"
        ),
        params_path: str = typer.Option(
            "source/params.json", help=""
        ),
        data_key: str = typer.Option(
            "", help="Вкладки: 'контроль' или 'Дих'"
        )
):
    extract_data(
        source_path=source_path,
        target_path=target_path,
        params_path=params_path,
        data_key=data_key
    )

@app.command()
def personal_data(
        source_path: str = typer.Option(
            "raw_data.json", help=""
        ),
        target_path: str = typer.Option(
            "personal_data.json", help=""
        )
):
    extract_personal_data(
        source_path=source_path,
        target_path=target_path
    )

@app.command()
def personal_indicators(
        source_path: str = typer.Option(
            "raw_data.json", help=""
        ),
        target_path: str = typer.Option(
            "personal_indicators.json", help=""
        )
):
    extract_personal_indicators(
        source_path=source_path,
        target_path=target_path
    )
