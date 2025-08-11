from app.infra.di import Container


def util_experiment_map_file(
        source_path: str,
        config_path: str
):
    container = Container()
    container.config.CONFIG_PATH.from_value(config_path)
    util_controller = container.util_controller()
    config_provider = container.config_provider()

    util_controller.experiment_map_file(
        source_path=source_path,
        config_provider=config_provider
    )

def util_export_experiment_data(
        source_path: str,
        config_path: str
):
    container = Container()
    container.config.CONFIG_PATH.from_value(config_path)
    util_controller = container.util_controller()
    config_provider = container.config_provider()

    util_controller.export_experiment_data(
        source_path=source_path,
        config_provider=config_provider
    )

def util_export_params_experiment_data(
        source_path: str,
        config_path: str
):
    container = Container()
    container.config.CONFIG_PATH.from_value(config_path)
    util_controller = container.util_controller()
    config_provider = container.config_provider()

    util_controller.export_params_experiment_data(
        source_path=source_path,
        config_provider=config_provider
    )
