import typer

from app.cli.handlers.import_handlers import import_from_google_sheets

app = typer.Typer()

@app.command()
def from_google_sheets(
        url: str = typer.Option(
            "https://docs.google.com/spreadsheets/d/1pof_7PrP8FiV8Y2qZFxswsn3O4a7RUd-aGJbc_FNGW4", help=""
        ),
        target_path: str = typer.Option(
            "source/raw_data.json", help=""
        )
):
    import_from_google_sheets(
        url=url,
        target_path=target_path
    )

@app.command()
def control_group(
        url: str = typer.Option(
            "https://docs.google.com/spreadsheets/d/1vxdtkTqkI9dlgB5HZ200ZPgu_ynxTIMHpMYGf_hCNBM", help=""
        ),
        target_path: str = typer.Option(
            "source/control_group_data.json", help=""
        )
):
    import_from_google_sheets(
        url=url,
        target_path=target_path
    )