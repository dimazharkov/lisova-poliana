from typing import Optional, Literal

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
        config_path: str,
        hue_field: str,
        effect_field: str = "median_effect",
        grouping_fields: Optional[list[str]] = None,
        test_type: Literal["paired", "independent"] = "independent"
):
    container = Container()
    container.config.SOURCE_PATHS.from_value(source_path)
    container.config.TARGET_PATH.from_value(target_folder)
    container.config.CONFIG_PATH.from_value(config_path)
    container.config.HUE_FIELD.from_value(hue_field)
    container.config.EFFECT_FIELD.from_value(effect_field)
    container.config.GROUPING_FIELDS.from_value(grouping_fields)
    container.config.FILTERS.from_value(
        {
            "experiment": int(experiment)
        }
    )
    container.config.TEST_TYPE.from_value(test_type)

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

def experiment_params_before_after(
        source_path: list[str],
        target_folder: str,
        experiment: str,
        config_path: str,
        test_type: Literal["paired", "independent"] = "independent"
):
    container = Container()
    container.config.SOURCE_PATHS.from_value(source_path)
    container.config.TARGET_PATH.from_value(target_folder)
    container.config.CONFIG_PATH.from_value(config_path)
    container.config.HUE_PARAM.from_value("repeat")
    container.config.FILTERS.from_value(
        {
            "experiment": int(experiment)
        }
    )
    container.config.TEST_TYPE.from_value(test_type)

    params_before_after_experiment_use_case = container.params_before_after_experiment_use_case()
    experiment_controller = container.experiment_controller()
    experiment_controller.run(params_before_after_experiment_use_case)

def experiment_params_delta_before_after(
        source_path: list[str],
        target_folder: str,
        experiment: str,
        config_path: str
):
    container = Container()
    container.config.SOURCE_PATHS.from_value(source_path)
    container.config.TARGET_PATH.from_value(target_folder)
    container.config.CONFIG_PATH.from_value(config_path)
    container.config.HUE_PARAM.from_value("treatment")
    container.config.FILTERS.from_value(
        {
            "experiment": int(experiment)
        }
    )

    params_before_after_experiment_use_case = container.params_before_after_experiment_use_case()
    experiment_controller = container.experiment_controller()
    experiment_controller.run(params_before_after_experiment_use_case)
