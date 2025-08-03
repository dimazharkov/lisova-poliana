from app.infra.di import Container


def experiment_baseline(
        source_path: list[str],
        target_folder: str
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

def experiment_before_after(
        source_path: list[str],
        target_folder: str,
        experiment: str,
        config_path: str
):
    container = Container()
    container.config.SOURCE_PATHS.from_value(source_path)
    container.config.TARGET_PATH.from_value(target_folder)
    container.config.CONFIG_PATH.from_value(config_path)
    container.config.FILTERS.from_value(
        {
            "experiment": int(experiment)
        }
    )

    before_after_experiment_use_case = container.before_after_experiment_use_case()
    experiment_controller = container.experiment_controller()
    experiment_controller.run(before_after_experiment_use_case)

def experiment_control_treatment(
        source_path: list[str],
        target_folder: str,
        experiment: str,
        config_path: str
):
    container = Container()
    container.config.SOURCE_PATHS.from_value(source_path)
    container.config.TARGET_PATH.from_value(target_folder)
    container.config.CONFIG_PATH.from_value(config_path)
    container.config.FILTERS.from_value(
        {
            "experiment": int(experiment)
        }
    )

    control_treatment_experiment_use_case = container.control_treatment_experiment_use_case()
    experiment_controller = container.experiment_controller()
    experiment_controller.run(control_treatment_experiment_use_case)
