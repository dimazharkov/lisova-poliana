from app.infra.di import Container


def import_from_google_sheets(
        url: str,
        target_path: str
):
    container = Container()
    import_controller = container.import_controller()
    import_controller.from_google_sheets(
        url, target_path
    )
